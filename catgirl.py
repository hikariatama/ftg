#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://img.icons8.com/color/480/000000/bt21-cooky.png
# meta developer: @hikarimods
# requires: requests
# scope: hikka_only
# scope: hikka_min 1.0.7

import asyncio
import functools

import requests
from telethon.tl.types import Message

from .. import loader, utils


async def photo(nsfw: bool) -> str:
    tag = "not_found"
    while tag == "not_found":
        try:
            img = (
                await utils.run_sync(
                    requests.get, "https://nekos.moe/api/v1/random/image"
                )
            ).json()["images"][0]
        except KeyError:
            await asyncio.sleep(1)
            continue

        tag = (
            "not_found"
            if img["nsfw"] and not nsfw or not img["nsfw"] and nsfw
            else "found"
        )

    return f'https://nekos.moe/image/{img["id"]}.jpg'


@loader.tds
class CatgirlMod(loader.Module):
    """Sends cute anime girl pictures"""

    strings = {"name": "Catgirl"}

    async def on_unload(self):
        asyncio.ensure_future(
            self._client.inline_query("@hikkamods_bot", "#statunload:catgirl")
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

        self.allmodules._hikari_stats += ["catgirl"]

        if not hasattr(self.allmodules, "_hikari_stats_task"):
            self.allmodules._hikari_stats_task = asyncio.ensure_future(
                self.stats_task()
            )

    async def catgirlcmd(self, message: Message):
        """[nsfw] - Send catgirl picture"""
        await self.inline.gallery(
            caption=lambda: f"<i>{utils.ascii_face()}</i>",
            message=message,
            next_handler=functools.partial(
                photo,
                nsfw="nsfw" in utils.get_args_raw(message).lower(),
            ),
            preload=5,
        )
