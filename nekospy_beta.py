__version__ = (2, 12, 3)

# ©️ Dan Gazizullin, 2021-2023
# This file is a part of Hikka Userbot
# Code is licensed under CC-BY-NC-ND 4.0 unless otherwise specified.
# 🌐 https://github.com/hikariatama/Hikka
# 🔑 https://creativecommons.org/licenses/by-nc-nd/4.0/
# + attribution
# + non-commercial
# + no-derivatives

# You CANNOT edit this file without direct permission from the author.
# You can redistribute this file without any changes.

# meta pic: https://0x0.st/oRer.webp
# meta banner: https://mods.hikariatama.ru/badges/nekospy_beta.jpg

# meta developer: @hikarimods
# scope: hikka_only
# scope: hikka_min 1.6.3
# requires: python-magic

# packurl: https://gist.github.com/hikariatama/a1bf9aa5aae566b9d07977fa55e18734/raw/368fdb3fe92508aee4eb7d68d3cb4311490b6aa8/nekospy.yml

import asyncio
import contextlib
import datetime
import io
import json
import logging
import mimetypes
import os
import re
import time
import typing
import zlib
from abc import ABC, abstractmethod
from pathlib import Path

import magic
from hikkatl.tl.types import (
    InputDocumentFileLocation,
    InputPhotoFileLocation,
    Message,
    UpdateDeleteChannelMessages,
    UpdateDeleteMessages,
    UpdateEditChannelMessage,
    UpdateEditMessage,
)
from hikkatl.utils import get_display_name

from .. import loader, utils
from ..database import Database
from ..pointers import PointerList
from ..tl_cache import CustomTelegramClient

logger = logging.getLogger(__name__)


def get_size(path: Path) -> int:
    return sum(f.stat().st_size for f in path.glob("**/*") if f.is_file())


def sizeof_fmt(num: int, suffix: str = "B") -> str:
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


class RecentsItem(typing.NamedTuple):
    timestamp: int
    chat_id: int
    message_id: int
    action: str

    @classmethod
    def from_edit(cls, message: Message) -> "RecentsItem":
        return cls(
            timestamp=int(time.time()),
            chat_id=utils.get_chat_id(message),
            message_id=message.id,
            action=ACTION_EDIT,
        )

    @classmethod
    def from_delete(
        cls,
        message_id: int,
        chat_id: typing.Optional[int] = None,
    ) -> "RecentsItem":
        return cls(
            timestamp=int(time.time()),
            chat_id=chat_id,
            message_id=message_id,
            action=ACTION_DELETE,
        )


ACTION_EDIT = "edit"
ACTION_DELETE = "del"


class CacheManager(ABC):
    @abstractmethod
    def purge(self):
        """Purge the cache"""

    @abstractmethod
    def stats(self) -> tuple:
        """Return cache statistics"""

    @abstractmethod
    def gc(self, max_age: int, max_size: int) -> None:
        """Clean the cache"""

    @abstractmethod
    async def store_message(
        self,
        message: Message,
        no_repeat: bool = False,
    ) -> typing.Union[bool, typing.Dict[str, typing.Any]]:
        """Store a message in the cache"""

    @abstractmethod
    async def fetch_message(
        self,
        chat_id: typing.Optional[int],
        message_id: int,
    ) -> typing.Optional[dict]:
        """Fetch a message from the cache"""


class CacheManagerDisc(CacheManager):
    def __init__(self, client: CustomTelegramClient, db: Database):
        self._client = client
        self._db = db
        self._cache_dir = Path.home().joinpath(".nekospy")
        self._cache_dir.mkdir(parents=True, exist_ok=True)

    def purge(self):
        for _file in self._cache_dir.iterdir():
            if _file.is_dir():
                for _child in _file.iterdir():
                    _child.unlink()

                _file.rmdir()

    def stats(self) -> tuple:
        dirsize = sizeof_fmt(get_size(self._cache_dir))
        messages_count = len(list(self._cache_dir.glob("**/*")))
        try:
            oldest_message = datetime.datetime.fromtimestamp(
                max(map(os.path.getctime, self._cache_dir.iterdir()))
            ).strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            oldest_message = "n/a"

        return dirsize, messages_count, oldest_message

    def gc(self, max_age: int, max_size: int) -> None:
        """Clean the cache"""
        for _file in self._cache_dir.iterdir():
            if _file.is_file():
                if _file.stat().st_mtime < time.time() - max_age:
                    _file.unlink()
            else:
                for _child in _file.iterdir():
                    if (
                        _child.is_file()
                        and _child.stat().st_mtime < time.time() - max_age
                    ):
                        _child.unlink()

        while get_size(self._cache_dir) > max_size:
            min(
                self._cache_dir.iterdir(),
                key=lambda x: x.stat().st_mtime,
            ).unlink()

    async def store_message(
        self,
        message: Message,
        no_repeat: bool = False,
    ) -> typing.Union[bool, typing.Dict[str, typing.Any]]:
        """Store a message in the cache"""
        if not hasattr(message, "id"):
            return False

        _dir = self._cache_dir.joinpath(str(utils.get_chat_id(message)))
        _dir.mkdir(parents=True, exist_ok=True)
        _file = _dir.joinpath(str(message.id))

        sender = None

        try:
            if message.sender_id is not None:
                try:
                    sender = await self._client.get_entity(message.sender_id, exp=0)
                except Exception:
                    sender = await message.get_sender()

            try:
                chat = await self._client.get_entity(utils.get_chat_id(message), exp=0)
            except Exception:
                chat = await message.get_chat()

            if message.sender_id is None:
                sender = chat
        except ValueError:
            if no_repeat:
                logger.debug("Failed to get sender/chat, skipping", exc_info=True)
                return False

            await asyncio.sleep(5)
            return await self.store_message(message, True)

        is_chat: bool = message.is_group or message.is_channel

        try:
            text: str = message.text
        except AttributeError:
            text: str = message.raw_text

        message_data = {
            "url": await utils.get_message_link(message),
            "text": text,
            "sender_id": sender.id if sender else None,
            "sender_bot": not not getattr(sender, "bot", False),
            "sender_name": utils.escape_html(get_display_name(sender)),
            "sender_url": utils.get_entity_url(sender),
            "chat_id": chat.id,
            **(
                {
                    "chat_name": utils.escape_html(get_display_name(chat)),
                    "chat_url": utils.get_entity_url(chat),
                }
                if is_chat
                else {}
            ),
            "assets": await self._extract_assets(message),
            "is_chat": is_chat,
            "via_bot_id": not not message.via_bot_id,
        }

        _file.write_bytes(zlib.compress(json.dumps(message_data).encode("utf-8")))
        return message_data

    async def fetch_message(
        self,
        chat_id: typing.Optional[int],
        message_id: int,
    ) -> typing.Optional[dict]:
        """Fetch a message from the cache"""
        _dir = None
        if chat_id:
            _dir = self._cache_dir.joinpath(str(chat_id))
            _file = _dir.joinpath(str(message_id))
        else:
            for _dir in self._cache_dir.iterdir():
                _file = _dir.joinpath(str(message_id))
                if _file.exists():
                    break
            else:
                _file = None

        if not _file or not _file.exists():
            return None

        data = json.loads(zlib.decompress(_file.read_bytes()).decode("utf-8"))
        data["chat_id"] = data["chat_id"] or int(_dir.name if _dir else 0)

        return data

    async def _extract_assets(self, message: Message) -> typing.Dict[str, str]:
        return {
            attribute: {
                "id": value.id,
                "access_hash": value.access_hash,
                "file_reference": bytearray(value.file_reference).hex(),
                "thumb_size": getattr(
                    value,
                    "thumb_size",
                    value.sizes[-1].type if getattr(value, "sizes", None) else "",
                ),
            }
            for attribute, value in filter(
                lambda x: x[1],
                {
                    arg: getattr(message, arg)
                    for arg in {
                        "photo",
                        "audio",
                        "document",
                        "sticker",
                        "video",
                        "voice",
                        "video_note",
                        "gif",
                    }
                }.items(),
            )
        }


@loader.tds
class NekoSpyBeta(loader.Module):
    """Sends you deleted and / or edited messages from selected users"""

    strings = {"name": "NekoSpy"}

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "enable_pm",
                True,
                lambda: self.strings("cfg_enable_pm"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "enable_groups",
                False,
                lambda: self.strings("cfg_enable_groups"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "whitelist",
                [],
                lambda: self.strings("cfg_whitelist"),
                validator=loader.validators.Hidden(loader.validators.Series()),
            ),
            loader.ConfigValue(
                "blacklist",
                [],
                lambda: self.strings("cfg_blacklist"),
                validator=loader.validators.Hidden(loader.validators.Series()),
            ),
            loader.ConfigValue(
                "always_track",
                [],
                lambda: self.strings("cfg_always_track"),
                validator=loader.validators.Hidden(loader.validators.Series()),
            ),
            loader.ConfigValue(
                "log_edits",
                True,
                lambda: self.strings("cfg_log_edits"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "ignore_inline",
                True,
                lambda: self.strings("cfg_ignore_inline"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "fw_protect",
                3.0,
                lambda: self.strings("cfg_fw_protect"),
                validator=loader.validators.Float(minimum=0.0),
            ),
            loader.ConfigValue(
                "save_sd",
                True,
                lambda: self.strings("cfg_save_sd"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "max_cache_size",
                1024 * 1024 * 1024,
                lambda: self.strings("max_cache_size"),
                validator=loader.validators.Integer(minimum=0),
            ),
            loader.ConfigValue(
                "max_cache_age",
                7 * 24 * 60 * 60,
                lambda: self.strings("max_cache_age"),
                validator=loader.validators.Integer(minimum=0),
            ),
            loader.ConfigValue(
                "recent_maximum",
                60 * 60,
                lambda: self.strings("recent_maximum"),
                validator=loader.validators.Integer(minimum=0),
            ),
            loader.ConfigValue(
                "nocache_big_chats",
                True,
                lambda: self.strings("cfg_nocache_big_chats"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "nocache_chats",
                [],
                lambda: self.strings("cfg_nocache_chats"),
                validator=loader.validators.Hidden(loader.validators.Series()),
            ),
            loader.ConfigValue(
                "ecospace_mode",
                False,
                lambda: self.strings("cfg_ecospace_mode"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "very_important",
                [],
                "Very important chats go here",
                validator=loader.validators.Hidden(loader.validators.Series()),
            ),
        )

        self._queue: typing.List[asyncio.coroutine] = []
        self._next: int = 0
        self._threshold: int = 10
        self._flood_protect_sample: int = 60
        self._channel: int = None
        self._tl_channel: int = None
        self._ignore_cache: typing.List[int] = []
        self.METHOD_MAP: typing.Dict[str, callable] = None
        self._cacher: CacheManager = None
        self._recent: typing.Dict[int, int] = {}

    async def client_ready(self):
        channel, _ = await utils.asset_channel(
            self._client,
            "hikka-nekospy",
            "Deleted and edited messages will appear there",
            silent=True,
            invite_bot=True,
            avatar="https://i.pinimg.com/originals/6c/1e/cf/6c1ecf3afca663a9ebc0b18788b337ee.jpg",
            _folder="hikka",
        )

        self._channel = int(f"-100{channel.id}")
        self._tl_channel = channel.id
        self.METHOD_MAP = {
            "photo": self.inline.bot.send_photo,
            "video": self.inline.bot.send_video,
            "voice": self.inline.bot.send_voice,
            "document": self.inline.bot.send_document,
        }

        self._cacher = CacheManagerDisc(self._client, self._db)
        self._gc.start()
        self._recent: PointerList = self.pointer(
            "recent_msgs",
            [],
            item_type=RecentsItem,
        )

    @loader.loop(interval=15)
    async def _gc(self):
        self._cacher.gc(self.config["max_cache_age"], self.config["max_cache_size"])
        for item in self._recent:
            if item.timestamp + self.config["recent_maximum"] < time.time():
                self._recent.remove(item)

    @loader.loop(interval=0.1, autostart=True)
    async def _sender(self):
        if not self._queue or self._next > time.time():
            return

        try:
            await self._queue.pop(0)
        except Exception:
            logger.exception("Failed to send message")

        self._next = int(time.time()) + self.config["fw_protect"]

    @staticmethod
    def _int(value: typing.Union[str, int], /) -> typing.Union[str, int]:
        return int(value) if str(value).isdigit() else value

    @property
    def blacklist(self):
        return list(
            map(
                self._int,
                self.config["blacklist"]
                + [777000, self._client.tg_id, self._tl_channel, self.inline.bot_id],
            )
        )

    @property
    def very_important(self):
        return list(
            map(
                self._int,
                self.config["very_important"],
            )
        )

    @blacklist.setter
    def blacklist(self, value: list):
        self.config["blacklist"] = list(
            set(value)
            - {777000, self._client.tg_id, self._tl_channel, self.inline.bot_id}
        )

    @property
    def whitelist(self):
        return list(map(self._int, self.config["whitelist"]))

    @whitelist.setter
    def whitelist(self, value: list):
        self.config["whitelist"] = value

    @property
    def always_track(self):
        return list(map(self._int, self.config["always_track"]))

    @loader.command()
    async def spymode(self, message: Message):
        """Toggle spymode"""
        await utils.answer(
            message,
            self.strings("state").format(
                self.strings("off" if self.get("state", False) else "on")
            ),
        )
        self.set("state", not self.get("state", False))

    @loader.command()
    async def spybl(self, message: Message):
        """Add / remove chat from blacklist"""
        chat = utils.get_chat_id(message)
        if chat in self.blacklist:
            self.blacklist = list(set(self.blacklist) - {chat})
            await utils.answer(message, self.strings("spybl_removed"))
        else:
            self.blacklist = list(set(self.blacklist) | {chat})
            await utils.answer(message, self.strings("spybl"))

    @loader.command()
    async def spyblclear(self, message: Message):
        """Clear blacklist"""
        self.blacklist = []
        await utils.answer(message, self.strings("spybl_clear"))

    @loader.command()
    async def spywl(self, message: Message):
        """Add / remove chat from whitelist"""
        chat = utils.get_chat_id(message)
        if chat in self.whitelist:
            self.whitelist = list(set(self.whitelist) - {chat})
            await utils.answer(message, self.strings("spywl_removed"))
        else:
            self.whitelist = list(set(self.whitelist) | {chat})
            await utils.answer(message, self.strings("spywl"))

    @loader.command()
    async def spywlclear(self, message: Message):
        """Clear whitelist"""
        self.whitelist = []
        await utils.answer(message, self.strings("spywl_clear"))

    async def _get_entities_list(self, entities: list) -> str:
        return "\n".join(
            [
                "\u0020\u2800\u0020\u2800<emoji"
                ' document_id=4971987363145188045>▫️</emoji> <b><a href="{}">{}</a></b>'
                .format(
                    utils.get_entity_url(await self._client.get_entity(x, exp=0)),
                    utils.escape_html(
                        get_display_name(await self._client.get_entity(x, exp=0))
                    ),
                )
                for x in entities
            ]
        )

    @loader.command()
    async def spyinfo(self, message: Message):
        """Show current spy mode configuration"""
        if not self.get("state"):
            await utils.answer(
                message,
                self.strings("mode_off").format(self.get_prefix()),
            )
            return

        info = ""

        if self.config["save_sd"]:
            info += self.strings("save_sd")

        if self.config["enable_groups"]:
            info += self.strings("chat")

        if self.config["enable_pm"]:
            info += self.strings("pm")

        if self.whitelist:
            info += self.strings("whitelist").format(
                await self._get_entities_list(self.whitelist)
            )

        if self.config["blacklist"]:
            info += self.strings("blacklist").format(
                await self._get_entities_list(self.config["blacklist"])
            )

        if self.always_track:
            info += self.strings("always_track").format(
                await self._get_entities_list(self.always_track)
            )

        await utils.answer(message, info)

    async def _notify_sticker(self, file: dict, caption: str):
        file["file_reference"] = bytes.fromhex(file["file_reference"])
        try:
            file = await self._client.download_file(
                InputDocumentFileLocation(**file),
                bytes,
            )
        except Exception:
            file = None

        if file:
            try:
                ext = (
                    mimetypes.guess_extension(magic.from_buffer(file, mime=True))
                    or ".bin"
                )
            except Exception:
                ext = ".bin"

            if ext == ".gz":
                ext = ".tgs"

            file = io.BytesIO(file)
            file.name = f"restored{ext}"

            m = await (
                self.inline.bot.send_video
                if ext == ".webm"
                else self.inline.bot.send_sticker
            )(self._channel, file)
        else:
            m = None

        await self.inline.bot.send_message(
            self._channel,
            caption + "\n&lt;sticker&gt;",
            reply_to_message_id=m.message_id if m else None,
        )

    async def _notify(self, msg_obj: dict, caption: str):
        caption = self.inline.sanitise_text(caption)
        for username in set(
            [username.username for username in (self._client.hikka_me.usernames or [])]
            + [self._client.hikka_me.username]
        ):
            caption = caption.replace(f"@{username}", f"<code>{username}</code>")

        assets = msg_obj["assets"]

        file = next((x for x in assets.values() if x), None)
        if not file:
            self._queue += [
                self.inline.bot.send_message(
                    self._channel,
                    caption,
                    disable_web_page_preview=True,
                )
            ]
            return

        if assets.get("sticker"):
            self._queue += [self._notify_sticker(file, caption)]
            return

        file["file_reference"] = bytes(bytearray.fromhex(file["file_reference"]))
        try:
            file = await self._client.download_file(
                (
                    InputPhotoFileLocation
                    if assets.get("photo") or assets.get("sticker")
                    else InputDocumentFileLocation
                )(**file),
                bytes,
            )
        except Exception:
            logger.exception("Can't restore file")
            self._queue += [
                self.inline.bot.send_message(
                    self._channel,
                    caption + "\n\n&lt;unable to restore file&gt;",
                    disable_web_page_preview=True,
                )
            ]
            return

        try:
            if not (
                ext := mimetypes.guess_extension(magic.from_buffer(file, mime=True))
            ):
                ext = ".bin"
        except Exception:
            ext = ".bin"

        file = io.BytesIO(file)
        file.name = f"restored{ext}"

        self._queue += [
            next(func for name, func in self.METHOD_MAP.items() if assets.get(name))(
                self._channel,
                file,
                caption=caption,
            )
        ]

    @loader.raw_handler(UpdateEditChannelMessage)
    async def channel_edit_handler(self, update: UpdateEditChannelMessage):
        self._recent.append(RecentsItem.from_edit(update.message))

        if (
            not self.get("state", False)
            or update.message.out
            or (self.config["ignore_inline"] and update.message.via_bot_id)
        ):
            return

        msg_obj = await self._cacher.fetch_message(
            utils.get_chat_id(update.message),
            update.message.id,
        )
        if (
            msg_obj
            and msg_obj["is_chat"]
            and (
                int(msg_obj["chat_id"]) in self.always_track
                or int(msg_obj["sender_id"]) in self.always_track
                or (
                    self.config["log_edits"]
                    and self.config["enable_groups"]
                    and utils.get_chat_id(update.message) not in self.blacklist
                    and (
                        not self.whitelist
                        or utils.get_chat_id(update.message) in self.whitelist
                    )
                )
            )
            and not msg_obj["sender_bot"]
            and update.message.raw_text != utils.remove_html(msg_obj["text"])
        ):
            await self._notify(
                msg_obj,
                self.strings("edited_chat").format(
                    msg_obj["chat_url"],
                    msg_obj["chat_name"],
                    msg_obj["sender_url"],
                    msg_obj["sender_name"],
                    msg_obj["text"],
                    message_url=msg_obj["url"],
                ),
            )

        await self._cacher.store_message(update.message)

    def _should_capture(self, user_id: int, chat_id: int) -> bool:
        return (
            chat_id not in self.blacklist
            and user_id not in self.blacklist
            and (
                not self.whitelist
                or chat_id in self.whitelist
                or user_id in self.whitelist
            )
        )

    @loader.raw_handler(UpdateEditMessage)
    async def pm_edit_handler(self, update: UpdateEditMessage):
        self._recent.append(RecentsItem.from_edit(update.message))

        if (
            not self.get("state", False)
            or update.message.out
            or (self.config["ignore_inline"] and update.message.via_bot_id)
        ):
            return

        msg_obj = await self._cacher.fetch_message(
            utils.get_chat_id(update.message),
            update.message.id,
        )

        if msg_obj:
            sender_id, chat_id, is_chat = (
                int(msg_obj["sender_id"]),
                int(msg_obj["chat_id"]),
                msg_obj["is_chat"],
            )

            if (
                (
                    sender_id in self.always_track
                    or chat_id in self.always_track
                    or (
                        (
                            self.config["log_edits"]
                            and self._should_capture(sender_id, chat_id)
                        )
                        and (
                            (
                                self.config["enable_pm"]
                                and not is_chat
                                or self.config["enable_groups"]
                                and is_chat
                            )
                        )
                    )
                )
                and update.message.raw_text != utils.remove_html(msg_obj["text"])
                and not msg_obj["sender_bot"]
            ):
                await self._notify(
                    msg_obj,
                    (
                        self.strings("edited_chat").format(
                            msg_obj["chat_url"],
                            msg_obj["chat_name"],
                            msg_obj["sender_url"],
                            msg_obj["sender_name"],
                            msg_obj["text"],
                            message_url=msg_obj["url"],
                        )
                        if is_chat
                        else self.strings("edited_pm").format(
                            msg_obj["sender_url"],
                            msg_obj["sender_name"],
                            msg_obj["text"],
                            message_url=msg_obj["url"],
                        )
                    ),
                )

        await self._cacher.store_message(update.message)

    @loader.raw_handler(UpdateDeleteMessages)
    async def pm_delete_handler(self, update: UpdateDeleteMessages):
        for message in update.messages:
            self._recent.append(RecentsItem.from_delete(message))

        if not self.get("state", False):
            return

        for message in update.messages:
            if not (
                msg_obj := await self._cacher.fetch_message(
                    chat_id=None,
                    message_id=message,
                )
            ):
                continue

            sender_id, chat_id, is_chat = (
                int(msg_obj["sender_id"]),
                int(msg_obj["chat_id"]),
                msg_obj["is_chat"],
            )

            if (
                sender_id not in self.always_track
                and chat_id not in self.always_track
                and (
                    not self._should_capture(sender_id, chat_id)
                    or (self.config["ignore_inline"] and msg_obj["via_bot_id"])
                    or (not self.config["enable_groups"] and is_chat)
                    or (not self.config["enable_pm"] and not is_chat)
                )
                or msg_obj["sender_bot"]
            ):
                continue

            await self._notify(
                msg_obj,
                (
                    self.strings("deleted_chat").format(
                        msg_obj["chat_url"],
                        msg_obj["chat_name"],
                        msg_obj["sender_url"],
                        msg_obj["sender_name"],
                        msg_obj["text"],
                        message_url=msg_obj["url"],
                    )
                    if is_chat
                    else self.strings("deleted_pm").format(
                        msg_obj["sender_url"],
                        msg_obj["sender_name"],
                        msg_obj["text"],
                        message_url=msg_obj["url"],
                    )
                ),
            )

    def _is_always_track(self, user_id: int, chat_id: int) -> bool:
        return chat_id in self.always_track or user_id in self.always_track

    @loader.raw_handler(UpdateDeleteChannelMessages)
    async def channel_delete_handler(self, update: UpdateDeleteChannelMessages):
        for message in update.messages:
            self._recent.append(RecentsItem.from_delete(message, update.channel_id))

        if not self.get("state", False):
            return

        for message in update.messages:
            if not message or not (
                msg_obj := await self._cacher.fetch_message(update.channel_id, message)
            ):
                continue

            sender_id, chat_id = (
                int(msg_obj["sender_id"]),
                int(msg_obj["chat_id"]),
            )

            if (
                self._is_always_track(sender_id, chat_id)
                or self.config["enable_groups"]
                and (
                    self._should_capture(sender_id, chat_id)
                    and (not self.config["ignore_inline"] or not msg_obj["via_bot_id"])
                    and not msg_obj["sender_bot"]
                )
            ):
                await self._notify(
                    msg_obj,
                    self.strings("deleted_chat").format(
                        msg_obj["chat_url"],
                        msg_obj["chat_name"],
                        msg_obj["sender_url"],
                        msg_obj["sender_name"],
                        msg_obj["text"],
                        message_url=msg_obj["url"],
                    ),
                )

    @loader.watcher("in", only_messages=True)
    async def watcher(self, message: Message):
        if not hasattr(message, "sender_id"):
            return

        if not hasattr(message, "sender"):
            message.sender = await message.get_sender()

        if (chat_id := utils.get_chat_id(message)) in self._ignore_cache or (
            message.is_private
            and self.config["ecospace_mode"]
            and (
                self.config["enable_pm"]
                and message.is_private
                and (
                    self._should_capture(message.sender_id, message.sender_id)
                    and (not self.config["ignore_inline"] or not message.via_bot_id)
                    and not message.sender.bot
                )
            )
        ):
            return

        for chat in self.config["nocache_chats"]:
            with contextlib.suppress(ValueError):
                if (await self._client.get_entity(chat, exp=0)).id == chat_id:
                    self._ignore_cache += [chat_id]
                    return

        if message.is_group:
            if self.config["ecospace_mode"] and not (
                self._is_always_track(message.sender_id, chat_id)
                or (
                    self.config["enable_groups"]
                    and message.is_group
                    and (
                        self._should_capture(message.sender_id, chat_id)
                        and (not self.config["ignore_inline"] or not message.via_bot_id)
                        and not message.sender.bot
                    )
                )
            ):
                return

            if (
                self.config["nocache_big_chats"]
                and (await self._client.get_participants(chat_id, limit=1)).total > 500
            ):
                self._ignore_cache += [chat_id]
                return

        msg_obj = await self._cacher.store_message(message)

        for chat in self.very_important:
            with contextlib.suppress(ValueError):
                if (
                    message.sender_id in self.very_important
                    or (await self._client.get_entity(chat, exp=0)).id == chat_id
                ):
                    if all(arg in msg_obj for arg in ("chat_url", "chat_name")):
                        await self._notify(
                            msg_obj,
                            self.strings("saved_chat").format(
                                msg_obj["chat_url"],
                                msg_obj["chat_name"],
                                msg_obj["sender_url"],
                                msg_obj["sender_name"],
                                msg_obj["text"],
                                message_url=msg_obj["url"],
                            ),
                        )
                    else:
                        await self._notify(
                            msg_obj,
                            self.strings("saved_pm").format(
                                msg_obj["sender_url"],
                                msg_obj["sender_name"],
                                msg_obj["text"],
                                message_url=msg_obj["url"],
                            ),
                        )

                    break

        if (
            not self.config["save_sd"]
            or not getattr(message, "media", False)
            or not getattr(message.media, "ttl_seconds", False)
        ):
            return

        media = io.BytesIO(await self.client.download_media(message.media, bytes))
        media.name = "sd.jpg" if message.photo else "sd.mp4"

        try:
            sender = await self.client.get_entity(message.sender_id, exp=0)
        except Exception:
            sender = await message.get_sender()

        await (
            self.inline.bot.send_photo if message.photo else self.inline.bot.send_video
        )(
            self._channel,
            media,
            caption=self.strings("sd_media").format(
                utils.get_entity_url(sender),
                utils.escape_html(get_display_name(sender)),
            ),
        )

    @loader.command()
    async def nssave(self, message: Message):
        """Save replied message to the channel"""

        async def _save(_reply: Message):
            msg_obj = await self._cacher.store_message(_reply)
            if all(arg in msg_obj for arg in ("chat_url", "chat_name")):
                await self._notify(
                    msg_obj,
                    self.strings("saved_chat").format(
                        msg_obj["chat_url"],
                        msg_obj["chat_name"],
                        msg_obj["sender_url"],
                        msg_obj["sender_name"],
                        msg_obj["text"],
                        message_url=msg_obj["url"],
                    ),
                )
            else:
                await self._notify(
                    msg_obj,
                    self.strings("saved_pm").format(
                        msg_obj["sender_url"],
                        msg_obj["sender_name"],
                        msg_obj["text"],
                        message_url=msg_obj["url"],
                    ),
                )

        if reply := await message.get_reply_message():
            await _save(reply)

        args = utils.get_args_raw(message)
        links = re.findall(r"(https://t.me[^\s]+)", args)

        for link in links:
            peer, msg = link.split("/")[-2:]
            msg = int(msg)
            if re.match(r"https://t.me/c/\d+/\d+", link):
                peer = int(peer)

            try:
                msg = (await self.client.get_messages(peer, ids=[msg]))[0]
                if not msg:
                    raise RuntimeError
            except Exception:
                logger.exception("Can't save message from link %s", link)
                continue

            await _save(msg)

        await utils.answer(message, self.strings("saved"))

    @loader.command()
    async def stat(self, message: Message):
        """Show stats for cached media and messages"""
        dirsize, messages_count, oldest_message = self._cacher.stats()
        await utils.answer(
            message,
            self.strings("stats").format(
                dirsize,
                messages_count,
                oldest_message,
            ),
        )

    @loader.command()
    async def purgecache(self, message: Message):
        """Empty cache storage from messages"""
        self._cacher.purge()
        self._recent.clear()
        await utils.answer(message, self.strings("purged_cache"))

    @loader.command()
    async def rest(self, message: Message):
        """[time] [-current] - Restore all deleted and edited messages from [time]"""
        args = utils.get_args_raw(message) or "5m"

        if "-current" in args:
            args = args.replace("-current", "").strip()
            from_chat = utils.get_chat_id(message)
        else:
            from_chat = None

        if args[-1].isdigit():
            args += "s"

        if args[-1] == "m":
            args = int(args[:-1]) * 60
        elif args[-1] == "s":
            args = int(args[:-1])
        elif args[-1] == "h":
            args = int(args[:-1]) * 60 * 60

        if args < 1:
            await utils.answer(message, self.strings("invalid_time"))
            return

        message = await utils.answer(message, self.strings("restoring"))
        for recent in self._recent:
            if (
                time.time() - recent.timestamp > args
                or not (
                    msg_obj := await self._cacher.fetch_message(
                        recent.chat_id,
                        recent.message_id,
                    )
                )
                or (from_chat and msg_obj.get("chat_id") != from_chat)
            ):
                continue

            if all(arg in msg_obj for arg in ("chat_url", "chat_name")):
                await self._notify(
                    msg_obj,
                    self.strings(
                        "deleted_chat"
                        if recent.action == ACTION_DELETE
                        else "edited_chat"
                    ).format(
                        msg_obj["chat_url"],
                        msg_obj["chat_name"],
                        msg_obj["sender_url"],
                        msg_obj["sender_name"],
                        msg_obj["text"],
                        message_url=msg_obj["url"],
                    ),
                )
            else:
                await self._notify(
                    msg_obj,
                    self.strings(
                        "deleted_pm" if recent.action == ACTION_DELETE else "edited_pm"
                    ).format(
                        msg_obj["sender_url"],
                        msg_obj["sender_name"],
                        msg_obj["text"],
                        message_url=msg_obj["url"],
                    ),
                )

        await utils.answer(message, self.strings("restored"))
