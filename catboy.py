# █ █ ▀ █▄▀ ▄▀█ █▀█ ▀    ▄▀█ ▀█▀ ▄▀█ █▀▄▀█ ▄▀█
# █▀█ █ █ █ █▀█ █▀▄ █ ▄  █▀█  █  █▀█ █ ▀ █ █▀█
#
#              © Copyright 2022
#
#          https://t.me/hikariatama
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://img.icons8.com/color/480/000000/tanjiro-kamado.png
# meta developer: @hikariatama
# requires: requests
# scope: hikka_only
# scope: hikka_min 1.0.7
# scope: inline

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

    async def client_ready(self, client, db):
        self._client = client

    async def catboycmd(self, message: Message):
        """Send catboy picture"""
        await self.inline.gallery(
            caption=lambda: f"<i>{utils.escape_html(utils.ascii_face())}</i>",
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
                    "caption": lambda: f"<i>Enjoy! {utils.escape_html(utils.ascii_face())}</i>",  # Optional
                    # Because of ^ this lambda, face will be generated every time the photo is switched
                    # "caption": f"<i>Enjoy! {utils.escape_html(utils.ascii_face())}</i>",
                    # If you make it without lambda ^, it will be generated once
                }
            ],
        )
