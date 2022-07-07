__version__ = (2, 0, 0)

# █ █ ▀ █▄▀ ▄▀█ █▀█ ▀    ▄▀█ ▀█▀ ▄▀█ █▀▄▀█ ▄▀█
# █▀█ █ █ █ █▀█ █▀▄ █ ▄  █▀█  █  █▀█ █ ▀ █ █▀█
#
#              © Copyright 2022
#
#          https://t.me/hikariatama
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://img.icons8.com/fluency/344/demolition-excavator.png
# meta developer: @hikarimods
# scope: hikka_only
# scope: hikka_min 1.1.12

import asyncio
import datetime
import logging
import re
import time

import requests
from telethon.tl.functions.channels import (
    CreateChannelRequest,
    DeleteChannelRequest,
    EditPhotoRequest,
)
from telethon.tl.functions.messages import ExportChatInviteRequest
from telethon.tl.types import Message

from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class TempChatsMod(loader.Module):
    """Creates temprorary chats"""

    strings = {
        "name": "TempChats",
        "chat_is_being_removed": "<b>🚫 This chat is being removed...</b>",
        "args": "🚫 <b>Check the args: </b><code>.help TempChats</code>",
        "chat_not_found": "🚫 <b>Chat not found</b>",
        "tmp_cancelled": "✅ <b>Chat </b><code>{}</code><b> will now live forever!</b>",
        "delete_error": "🚫 <b>An error occured while deleting this temp chat. Remove it manually.</b>",
        "temp_chat_header": "<b>⚠️ This chat</b> (<code>{}</code>)<b> is temporary and will be removed {}.</b>",
        "chat_created": '✅ <b><a href="{}">Chat</a> have been created</b>',
        "delete_error_me": "🚫 <b>Error occured while deleting chat {}</b>",
    }

    strings_ru = {
        "chat_is_being_removed": "<b>🚫 Чат удаляется...</b>",
        "args": "🚫 <b>Капец с аргументами: </b><code>.help TempChats</code>",
        "chat_not_found": "🚫 <b>Чат не найден</b>",
        "tmp_cancelled": "🚫 <b>Чат </b><code>{}</code><b> будет жить вечно!</b>",
        "delete_error": "🚫 <b>Произошла ошибка удаления чата. Сделай это вручную.</b>",
        "temp_chat_header": "<b>⚠️ Этот чат</b> (<code>{}</code>)<b> является временным и будет удален {}.</b>",
        "chat_created": '✅ <b><a href="{}">Чат</a> создан</b>',
        "delete_error_me": "🚫 <b>Ошибка удаления чата {}</b>",
        "_cmd_doc_tmpchat": "<время> <название> - Создать новый временный чат",
        "_cmd_doc_tmpcurrent": "<время> - Создать новый временный чат",
        "_cmd_doc_tmpchats": "Показать временные чаты",
        "_cmd_doc_tmpcancel": "[chat-id] - Отменить удаление чата.",
        "_cmd_doc_tmpctime": "<chat_id> <новое время> - Изменить время жизни чата",
        "_cls_doc": "Создает временные чаты во избежание мусорки в Телеграме.",
    }

    @staticmethod
    def s2time(t: str) -> int:
        """
        Tries to export time from text
        """
        try:
            if not str(t)[:-1].isdigit():
                return 0

            if "d" in str(t):
                t = int(t[:-1]) * 60 * 60 * 24

            if "h" in str(t):
                t = int(t[:-1]) * 60 * 60

            if "m" in str(t):
                t = int(t[:-1]) * 60

            if "s" in str(t):
                t = int(t[:-1])

            t = int(re.sub(r"[^0-9]", "", str(t)))
        except ValueError:
            return 0

        return t

    @loader.loop(interval=0.5, autostart=True)
    async def chats_handler_async(self):
        for chat, info in self.get("chats", {}).copy().items():
            if int(info[0]) > time.time():
                continue

            try:
                await self._client.send_message(
                    int(chat),
                    self.strings("chat_is_being_removed"),
                )
                await asyncio.sleep(1)
                await self._client(DeleteChannelRequest(int(chat)))
            except Exception:
                logger.exception("Failed to delete chat")
                await self.inline.bot.send_message(
                    self._tg_id,
                    self.strings("delete_error_me").format(utils.escape_html(info[1])),
                    parse_mode="HTML",
                    disable_web_page_preview=True,
                )

            chats = self.get("chats")
            del chats[chat]
            self.set("chats", chats)

    async def on_unload(self):
        asyncio.ensure_future(
            self._client.inline_query("@hikkamods_bot", "#statunload:temp_chat")
        )

    async def stats_task(self):
        await asyncio.sleep(60)
        await self._client.inline_query(
            "@hikkamods_bot",
            f"#statload:{','.join(list(set(self.allmodules._hikari_stats)))}",
        )
        delattr(self.allmodules, "_hikari_stats")
        delattr(self.allmodules, "_hikari_stats_task")

    async def client_ready(self, client, db):
        self._db = db
        self._client = client

        if not hasattr(self.allmodules, "_hikari_stats"):
            self.allmodules._hikari_stats = []

        self.allmodules._hikari_stats += ["temp_chat"]

        if not hasattr(self.allmodules, "_hikari_stats_task"):
            self.allmodules._hikari_stats_task = asyncio.ensure_future(
                self.stats_task()
            )

    async def tmpchatcmd(self, message: Message):
        """<time> <title> - Create new temp chat"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings("args"))
            return

        if len(args.split()) < 2:
            await utils.answer(message, self.strings("args"))
            return

        temp_time = args.split()[0]
        tit = args.split(maxsplit=1)[1].strip()

        until = self.s2time(temp_time)
        if not until:
            await utils.answer(message, self.strings("args"))
            return

        res = (
            await self._client(
                CreateChannelRequest(
                    tit,
                    "Temporary chat",
                    megagroup=True,
                )
            )
        ).chats[0]

        await self._client(
            EditPhotoRequest(
                channel=res,
                photo=await self._client.upload_file(
                    (
                        await utils.run_sync(
                            requests.get,
                            f"https://avatars.dicebear.com/api/adventurer-neutral/{utils.rand(10)}.png",
                        )
                    ).content,
                    file_name="photo.png",
                ),
            )
        )

        link = (await self._client(ExportChatInviteRequest(res))).link

        await utils.answer(message, self.strings("chat_created").format(link))
        cid = res.id

        await self._client.send_message(
            cid,
            self.strings("temp_chat_header").format(
                cid,
                datetime.datetime.utcfromtimestamp(
                    time.time() + until + 10800
                ).strftime("%d.%m.%Y %H:%M:%S"),
            ),
        )
        self.set(
            "chats", {**self.get("chats", {}), **{str(cid): [until + time.time(), tit]}}
        )

    async def tmpcurrentcmd(self, message: Message):
        """<time> - Make current chat temporary"""
        args = utils.get_args_raw(message)
        if not args or not self.s2time(args):
            await utils.answer(message, self.strings("args"))
            return

        until = self.s2time(args)
        cid = utils.get_chat_id(message)

        await utils.answer(
            message,
            self.strings("temp_chat_header").format(
                cid,
                datetime.datetime.utcfromtimestamp(
                    time.time() + until + 10800
                ).strftime("%d.%m.%Y %H:%M:%S"),
            ),
        )
        self.set(
            "chats",
            {
                **self.get("chats", {}),
                **{
                    str(cid): [
                        until + time.time(),
                        (await self._client.get_entity(cid)).title,
                    ]
                },
            },
        )

    async def tmpchatscmd(self, message: Message):
        """List temp chats"""
        res = "<b>⏱ Temporary Chats</b>\n"
        for chat, info in self.get("chats", {}).items():
            res += f'<b>{info[1]}</b> (<code>{chat}</code>)<b>: {datetime.datetime.utcfromtimestamp(info[0] + 10800).strftime("%d.%m.%Y %H:%M:%S")}.</b>\n'

        await utils.answer(message, res)

    async def tmpcancelcmd(self, message: Message):
        """[chat-id] - Disable deleting chat by id, or current chat if unspecified."""
        args = utils.get_args_raw(message)
        if args not in self.get("chats"):
            args = str(utils.get_chat_id(message))

        if args not in self.get("chats"):
            await utils.answer(message, self.strings("chat_not_found"))
            return

        await utils.answer(
            message,
            self.strings("tmp_cancelled").format(
                utils.escape_html(self.chats[args][1])
            ),
        )
        chats = self.get("chats")
        del chats[args]
        self.set("chats", chats)

    async def tmpctimecmd(self, message: Message):
        """<chat_id> <new_time> - Change chat deletion time"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings("args"))
            return

        args = args.split()

        if len(args) >= 2:
            chat = args[0]
            new_time = self.s2time(args[1])
        else:
            chat = str(utils.get_chat_id(message))
            new_time = self.s2time(args[0])

        if chat not in self.get("chats"):
            await utils.answer(message, self.strings("chat_not_found"))
            return

        chats = self.get("chats")
        chats[chat][0] = new_time
        self.set("chats", chats)
