#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://img.icons8.com/stickers/500/000000/naruto.png
# meta developer: @hikarimods
# scope: hikka_only

import asyncio
import logging
from random import choice

from telethon.tl.types import Message

from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class AnimatedQuotesMod(loader.Module):
    """Simple module to create animated stickers via bot"""

    strings = {
        "name": "AnimatedQuotes",
        "no_text": "🚫 <b>Provide a text to create sticker with</b>",
        "processing": "⏱ <b>Processing...</b>",
    }

    strings_ru = {
        "no_text": "🚫 <b>Укажи текст для создания стикера</b>",
        "processing": "⏱ <b>Обработка...</b>",
        "_cmd_doc_aniq": "<text> - Создать анимированный стикер",
        "_cls_doc": "Простенький модуль, который создает анимированные стикеры",
    }

    async def on_unload(self):
        asyncio.ensure_future(
            self._client.inline_query("@hikkamods_bot", "#statunload:aniquotes")
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
        self._client = client

        if not hasattr(self.allmodules, "_hikari_stats"):
            self.allmodules._hikari_stats = []

        self.allmodules._hikari_stats += ["aniquotes"]

        if not hasattr(self.allmodules, "_hikari_stats_task"):
            self.allmodules._hikari_stats_task = asyncio.ensure_future(
                self.stats_task()
            )

    async def aniqcmd(self, message: Message):
        """<text> - Create animated quote"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings("no_text"))
            return

        message = await utils.answer(message, self.strings("processing"))

        try:
            query = await self._client.inline_query("@QuotAfBot", args)
            await message.respond(file=choice(query).document)
        except Exception as e:
            await utils.answer(message, str(e))
            return

        if message.out:
            await message.delete()
