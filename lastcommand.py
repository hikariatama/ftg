#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://img.icons8.com/fluency/240/000000/last-48-hours.png
# meta developer: @hikarimods

import asyncio
from telethon.tl.types import Message

from .. import loader


@loader.tds
class LastCommandMod(loader.Module):
    """Execute last command"""

    strings = {"name": "LastCommand"}

    async def on_unload(self):
        asyncio.ensure_future(
            self._client.inline_query("@hikkamods_bot", "#statunload:lastcommand")
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

        self.allmodules._hikari_stats += ["lastcommand"]

        if not hasattr(self.allmodules, "_hikari_stats_task"):
            self.allmodules._hikari_stats_task = asyncio.ensure_future(
                self.stats_task()
            )
        orig_dispatch = self.allmodules.dispatch

        def _disp_wrap(command):
            txt, func = orig_dispatch(command)
            if "lc" not in txt:
                self.allmodules.last_command = func
            return txt, func

        self.allmodules.dispatch = _disp_wrap

    async def lccmd(self, message: Message):
        """Execute last command"""
        await self.allmodules.last_command(message)
