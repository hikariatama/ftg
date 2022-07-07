#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://img.icons8.com/color/480/000000/tanjiro-kamado.png
# meta developer: @hikarimods
# requires: requests
# scope: hikka_only
# scope: hikka_min 1.0.7
# scope: inline

import asyncio
from os import stat
import requests
from telethon.tl.types import Message

from .. import loader, utils
from ..inline.types import InlineQuery


async def photo() -> str:
    return (
        await utils.run_sync(
            requests.get,
            "https://api.catboys.com/img",
        )
    ).json()["url"]


@loader.tds
class CatboyMod(loader.Module):
    """Sends cute anime boy pictures"""

    strings = {"name": "Catboy"}

    async def on_unload(self):
        asyncio.ensure_future(
            self._client.inline_query("@hikkamods_bot", "#statunload:catboy")
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

        self.allmodules._hikari_stats += ["catboy"]

        if not hasattr(self.allmodules, "_hikari_stats_task"):
            self.allmodules._hikari_stats_task = asyncio.ensure_future(
                self.stats_task()
            )

    async def catboycmd(self, message: Message):
        """Send catboy picture"""
        await self.inline.gallery(
            caption=lambda: f"<i>{utils.ascii_face()}</i>",
            message=message,
            next_handler=photo,
            preload=5,
        )

    async def catboy_inline_handler(self, query: InlineQuery):
        """
        Send Catboys
        """
        await self.inline.query_gallery(
            query,
            [
                {
                    "title": "👩‍🎤 Catboy",
                    "description": "Send catboy photo",
                    "next_handler": photo,
                    "thumb_handler": photo,  # Optional
                    "caption": lambda: f"<i>Enjoy! {utils.ascii_face()}</i>",  # Optional
                    # Because of ^ this lambda, face will be generated every time the photo is switched
                    # "caption": f"<i>Enjoy! {utils.ascii_face()}</i>",
                    # If you make it without lambda ^, it will be generated once
                }
            ],
        )
