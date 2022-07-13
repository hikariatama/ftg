#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# scope: hikka_min 1.2.10

# meta pic: https://img.icons8.com/color/480/000000/bt21-cooky.png
# meta developer: @hikarimods
# requires: requests
# scope: hikka_only

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
