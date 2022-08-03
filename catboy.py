#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://static.hikari.gay/catboy_icon.png
# meta banner: https://mods.hikariatama.ru/badges/catboy.jpg
# meta developer: @hikarimods
# scope: inline
# scope: hikka_only
# scope: hikka_min 1.3.0

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

    @loader.command(ru_doc="Показать кошкомальчика")
    async def catboycmd(self, message: Message):
        """Send catboy picture"""
        await self.inline.gallery(
            caption=lambda: f"<i>{utils.ascii_face()}</i>",
            message=message,
            next_handler=photo,
            preload=5,
        )

    @loader.inline_handler(ru_doc="Показать кошкомальчиков")
    async def catboy(self, query: InlineQuery):
        """Send Catboys"""
        await self.inline.query_gallery(
            query,
            [
                {
                    "title": "👩‍🎤 Catboy",
                    "description": "Send catboy photo",
                    "next_handler": photo,
                    "thumb_handler": photo,
                    "caption": lambda: f"<i>Enjoy! {utils.ascii_face()}</i>",
                }
            ],
        )
