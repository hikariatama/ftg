#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://img.icons8.com/color/480/000000/dota.png
# meta developer: @hikarimods
# scope: inline
# scope: hikka_only
# scope: hikka_min 1.1.6

import asyncio
from telethon.tl.types import Message

from .. import loader


@loader.tds
class InlineGhoulMod(loader.Module):
    """Non-spammy ghoul module"""

    strings = {"name": "InlineGhoul", "tired": "😾 <b>Tired of counting!</b>"}

    strings_ru = {
        "tired": "😾 <b>Я устал считать!</b>",
        "_cmd_doc_ghoul": "Отправляет сообщение Гуля",
        "_cls_doc": "Неспамящий модуль Гуль",
    }

    async def on_unload(self):
        asyncio.ensure_future(
            self._client.inline_query("@hikkamods_bot", "#statunload:inline_ghoul")
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

        self.allmodules._hikari_stats += ["inline_ghoul"]

        if not hasattr(self.allmodules, "_hikari_stats_task"):
            self.allmodules._hikari_stats_task = asyncio.ensure_future(
                self.stats_task()
            )

    async def ghoulcmd(self, message: Message):
        """Sends ghoul message"""
        await self.animate(
            message,
            [f"👊 <b>{x} - 7 = {x - 7}</b>" for x in range(1000, 900, -7)]
            + [self.strings("tired")],
            interval=1,
            inline=True,
        )
