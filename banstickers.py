#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒 Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://img.icons8.com/fluency/344/cancel-2.png
# meta developer: @hikarimods
# meta banner: https://mods.hikariatama.ru/badges/banstickers.jpg
# scope: hikka_only
# scope: hikka_min 1.3.3
# requires: aiofile Pillow

import asyncio
import io
import time
from .. import loader, utils
import logging
import os
from aiofile import async_open
from PIL import ImageChops, Image
import math
import operator
from functools import reduce

from telethon.tl.types import Message
from telethon.tl.functions.messages import GetStickerSetRequest

logger = logging.getLogger(__name__)


@loader.tds
class BanStickers(loader.Module):
    """Bans stickerpacks, stickers and gifs in chat"""

    strings = {
        "name": "BanStickers",
        "args": (
            "<emoji document_id='5436162517686557387'>😵</emoji> <b>Reply to sticker is"
            " required</b>"
        ),
        "sticker_banned": (
            "<emoji document_id='6037557968914877661'>🛡</emoji> <b>This sticker is now"
            " banned in current chat</b>"
        ),
        "pack_banned": (
            "<emoji document_id='6037557968914877661'>🛡</emoji> <b>{} sticker(-s) from"
            " pack {} are now banned in current chat</b>"
        ),
        "wait": (
            "<emoji document_id='5451732530048802485'>⏳</emoji> <b>Banning stickers"
            " from this pack in current chat...</b>"
        ),
        "sticker_not_banned": (
            "<emoji document_id='5436162517686557387'>😵</emoji> <b>This sticker is not"
            " banned in current chat</b>"
        ),
        "sticker_unbanned": (
            "<emoji document_id='5472308992514464048'>🔐</emoji> <b>This sticker is no"
            " longer banned in current chat</b>"
        ),
        "pack_unbanned": (
            "<emoji document_id='5472308992514464048'>🔐</emoji> <b>{} / {} sticker(-s)"
            " from pack {} are no longer banned in current chat</b>"
        ),
        "pack_not_banned": (
            "<emoji document_id='5436162517686557387'>😵</emoji> <b>This pack is not"
            " banned in current chat</b>"
        ),
        "no_restrictions": (
            "<emoji document_id='5436040291507247633'>🎉</emoji> <b>This chat has"
            " no restrictions</b>"
        ),
        "all_unbanned": (
            "<emoji document_id='5472308992514464048'>🔐</emoji> <b>All stickers are"
            " unbanned in current chat</b>"
        ),
        "already_restricted": (
            "<emoji document_id='5436040291507247633'>🎉</emoji> <b>Animated and video"
            " stickers are already restricted</b>"
        ),
        "not_restricted": (
            "<emoji document_id='5436040291507247633'>🎉</emoji> <b>Animated stickers"
            " are not restricted</b>"
        ),
        "animations_restricted": (
            "<emoji document_id='5472308992514464048'>🔐</emoji> <b>Animated and video"
            " stickers are now restricted in current chat</b>"
        ),
        "animations_unrestricted": (
            "<emoji document_id='5472308992514464048'>🔐</emoji> <b>Animated stickers"
            " are no longer restricted</b>"
        ),
    }

    strings_ru = {
        "args": (
            "<emoji document_id='5436162517686557387'>😵</emoji> <b>Нужен ответ на"
            " стикер</b>"
        ),
        "sticker_banned": (
            "<emoji document_id='6037557968914877661'>🛡</emoji> <b>Этот стикер теперь"
            " запрещен в текущем чате</b>"
        ),
        "pack_banned": (
            "<emoji document_id='6037557968914877661'>🛡</emoji> <b>{} стикер(-ов) из"
            " пака {} теперь запрещены в текущем чате</b>"
        ),
        "wait": (
            "<emoji document_id='5451732530048802485'>⏳</emoji> <b>Запрещаю"
            " стикеры из этого пака в текущем чате...</b>"
        ),
        "sticker_not_banned": (
            "<emoji document_id='5436162517686557387'>😵</emoji> <b>Этот стикер не"
            " запрещен в текущем чате</b>"
        ),
        "sticker_unbanned": (
            "<emoji document_id='5472308992514464048'>🔐</emoji> <b>Этот стикер больше"
            " не запрещен в текущем чате</b>"
        ),
        "pack_unbanned": (
            "<emoji document_id='5472308992514464048'>🔐</emoji> <b>{} / {} стикер(-ов)"
            " из пака {} больше не запрещены в текущем чате</b>"
        ),
        "pack_not_banned": (
            "<emoji document_id='5436162517686557387'>😵</emoji> <b>Этот пак не запре"
            "щен в текущем чате</b>"
        ),
        "no_restrictions": (
            "<emoji document_id='5436040291507247633'>🎉</emoji> <b>В текущем чате нет"
            " ограничений</b>"
        ),
        "all_unbanned": (
            "<emoji document_id='5472308992514464048'>🔐</emoji> <b>Все стикеры"
            " разблокированы в текущем чате</b>"
        ),
        "already_restricted": (
            "<emoji document_id='5436040291507247633'>🎉</emoji> <b>Анимированные и"
            " видео стикеры уже запрещены</b>"
        ),
        "not_restricted": (
            "<emoji document_id='5436040291507247633'>🎉</emoji> <b>Анимированные"
            " стикеры не запрещены</b>"
        ),
        "animations_restricted": (
            "<emoji document_id='5472308992514464048'>🔐</emoji> <b>Анимированные и"
            " видео стикеры запрещены в текущем чате</b>"
        ),
        "animations_unrestricted": (
            "<emoji document_id='5472308992514464048'>🔐</emoji> <b>Анимированные"
            " стикеры больше не запрещены</b>"
        ),
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "rms_threshold",
                4.0,
                "The lower this value is - the more light the detection will be. 0.0 -"
                " Full match, 4.0 - approximate match",
                validator=loader.validators.Float(maximum=10.0),
            ),
            loader.ConfigValue(
                "bantime",
                180,
                "Once the user sent forbidden sticker, he will be restricted from"
                " sending more for this amount of seconds",
                validator=loader.validators.Integer(minimum=60),
            ),
        )

    async def client_ready(self):
        self._banlist = self.pointer("banlist", {})
        self._bananim = self.pointer("bananim", [])
        dir_path = os.path.abspath(
            os.path.join(utils.get_base_dir(), "..", "loaded_modules")
        )
        if not os.path.isdir(dir_path):
            os.mkdir(dir_path)

        dir_path = os.path.join(dir_path, "banmedia")
        if not os.path.isdir(dir_path):
            os.mkdir(dir_path)

        self._db_path = dir_path
        self._cache = {}
        self._filecache = {}
        for file in os.listdir(self._db_path):
            async with async_open(os.path.join(self._db_path, file), "rb") as f:
                self._cache[file] = await f.read()

    @staticmethod
    def rmsdiff(image_1: Image, image_2: Image) -> float:
        "Calculate the root-mean-square difference between two images"
        # https://stackoverflow.com/a/11818358/19170642

        try:
            h = ImageChops.difference(image_1, image_2).histogram()
        except ValueError:
            return 100.0

        return math.sqrt(
            reduce(operator.add, map(lambda h, i: h * (i**2), h, range(256)))
            / (float(image_1.size[0]) * image_1.size[1])
        )

    async def _add_cache(self, sticker_id: int, bytes_: bytes):
        if not os.path.isfile(os.path.join(self._db_path, str(sticker_id))):
            async with async_open(
                os.path.join(self._db_path, str(sticker_id)), "wb"
            ) as f:
                await f.write(bytes_)

        self._cache[str(sticker_id)] = bytes_

    async def _remove_cache(self, sticker_id: int):
        if os.path.isfile(os.path.join(self._db_path, str(sticker_id))):
            os.remove(os.path.join(self._db_path, str(sticker_id)))

        if str(sticker_id) in self._cache:
            self._cache.pop(str(sticker_id))

    @loader.command(ru_doc="<ответ на стикер> - Запретить стикер в текущем чате")
    async def banstick(self, message: Message):
        """<reply to sticker> - Ban sticker in current chat"""
        reply = await message.get_reply_message()
        if not reply or not reply.sticker:
            await utils.answer(message, self.strings("args"))
            return

        chat_id = str(utils.get_chat_id(message))
        self._banlist.setdefault(chat_id, []).append(reply.sticker.id)
        self._banlist[chat_id] = list(set(self._banlist[chat_id]))

        await self._add_cache(reply.sticker.id, await reply.download_media(bytes))
        await utils.answer(message, self.strings("sticker_banned"))

    @loader.command(
        ru_doc="<ответ на стикер> - Запретить весь стикерпак в текущем чате"
    )
    async def banpack(self, message: Message):
        """<reply to sticker> - Ban the whole stickerpack in current chat"""
        reply = await message.get_reply_message()
        if not reply or not reply.sticker:
            await utils.answer(message, self.strings("args"))
            return

        message = await utils.answer(message, self.strings("wait"))
        stickerset = await self._client(
            GetStickerSetRequest(
                next(
                    attr.stickerset
                    for attr in reply.sticker.attributes
                    if hasattr(attr, "stickerset")
                ),
                hash=0,
            )
        )

        stickers = stickerset.documents
        chat_id = str(utils.get_chat_id(message))

        for sticker in stickers:
            self._banlist.setdefault(chat_id, []).append(sticker.id)
            await self._add_cache(
                sticker.id,
                await self._client.download_file(sticker, bytes),
            )
            await asyncio.sleep(1)  # Light FW protection

        self._banlist[chat_id] = list(set(self._banlist[chat_id]))

        await utils.answer(
            message,
            self.strings("pack_banned").format(
                len(stickers),
                utils.escape_html(stickerset.set.title),
            ),
        )

    @loader.command(ru_doc="<ответ на стикер> - Разбанить стикер в текущем чате")
    async def unbanstick(self, message: Message):
        """<reply to sticker> - Unban sticker in current chat"""
        reply = await message.get_reply_message()
        if not reply or not reply.sticker:
            await utils.answer(message, self.strings("args"))
            return

        chat_id = str(utils.get_chat_id(message))
        if reply.sticker.id not in self._banlist.get(chat_id, []):
            await utils.answer(message, self.strings("sticker_not_banned"))
            return

        self._banlist[chat_id].remove(reply.sticker.id)
        await self._remove_cache(reply.sticker.id)

        await utils.answer(message, self.strings("sticker_unbanned"))

    @loader.command(
        ru_doc="<ответ на стикер> - Разбанить весь стикерпак в текущем чате"
    )
    async def unbanpack(self, message: Message):
        """<reply to sticker> - Unban the whole stickerpack in current chat"""
        reply = await message.get_reply_message()
        if not reply or not reply.sticker:
            await utils.answer(message, self.strings("args"))
            return

        message = await utils.answer(message, self.strings("wait"))
        stickerset = await self._client(
            GetStickerSetRequest(
                next(
                    attr.stickerset
                    for attr in reply.sticker.attributes
                    if hasattr(attr, "stickerset")
                ),
                hash=0,
            )
        )

        stickers = stickerset.documents
        chat_id = str(utils.get_chat_id(message))

        unbanned = 0

        for sticker in stickers:
            if sticker.id in self._banlist.get(chat_id, []):
                self._banlist[chat_id].remove(sticker.id)
                await self._remove_cache(sticker.id)
                unbanned += 1

        if not unbanned:
            await utils.answer(message, self.strings("pack_not_banned"))
            return

        await utils.answer(
            message,
            self.strings("pack_unbanned").format(
                unbanned,
                len(stickers),
                utils.escape_html(stickerset.set.title),
            ),
        )

    @loader.command(ru_doc="Убрать все ограничения в текущем чате")
    async def unbanall(self, message: Message):
        """Remove all restrictions in current chat"""
        chat_id = str(utils.get_chat_id(message))
        if not self._banlist.get(chat_id, []):
            await utils.answer(message, self.strings("no_restrictions"))
            return

        for sticker in self._banlist.pop(chat_id):
            await self._remove_cache(sticker)

        await utils.answer(message, self.strings("all_unbanned"))

    @loader.command(ru_doc="Запретить анимированные и видео стикеры в этом чате")
    async def bananim(self, message: Message):
        """Restrict animated stickers in current chat"""
        chat_id = str(utils.get_chat_id(message))
        if chat_id in self._bananim:
            await utils.answer(message, self.strings("already_restricted"))
            return

        self._bananim.append(chat_id)
        await utils.answer(message, self.strings("animations_restricted"))

    @loader.command(ru_doc="Разблокировать анимированные и видео стикеры в этом чате")
    async def unbananim(self, message: Message):
        """Unrestrict animated stickers in current chat"""
        chat_id = str(utils.get_chat_id(message))
        if chat_id not in self._bananim:
            await utils.answer(message, self.strings("not_restricted"))
            return

        self._bananim.remove(chat_id)
        await utils.answer(message, self.strings("animations_unrestricted"))

    @loader.watcher("in", only_stickers=True, only_groups=True)
    async def watcher(self, message: Message):
        chat_id = str(utils.get_chat_id(message))
        if not self._banlist.get(chat_id):
            return

        async def _restrict():
            nonlocal message
            await message.delete()
            await self._client.edit_permissions(
                message.peer_id,
                message.sender_id,
                until_date=time.time() + self.config["bantime"],
                send_stickers=False,
            )

        if not message.sticker.mime_type.startswith("image"):
            if chat_id in self._bananim:
                await _restrict()

            return

        if message.sticker.id in self._banlist[chat_id]:
            return await _restrict()

        if message.sticker.id in self._filecache:
            file = self._filecache[message.sticker.id]
        else:
            file = await message.download_media(bytes)
            self._filecache[message.sticker.id] = file

        image = Image.open(io.BytesIO(file))
        for sticker_id, bytes_ in self._cache.items():
            res = await utils.run_sync(
                self.rmsdiff,
                image,
                Image.open(io.BytesIO(bytes_)),
            )
            if res < self.config["rms_threshold"]:
                await self._add_cache(sticker_id, file)
                return await _restrict()
