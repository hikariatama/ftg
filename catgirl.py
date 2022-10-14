#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://static.hikari.gay/catgirl_icon.png
# meta banner: https://mods.hikariatama.ru/badges/catgirl.jpg
# meta developer: @hikarimods
# scope: hikka_only
# scope: hikka_min 1.2.10

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
    strings_ru = {"_cls_doc": "Отправляет милые фотографии аниме девочек"}
    strings_de = {"_cls_doc": "Sendet Anime-Katzenmädchen-Bilder"}
    strings_uz = {"_cls_doc": "Anime qiz rasmlarini jo'natadi"}
    strings_hi = {"_cls_doc": "एक एनीमे कैटगर्ल तस्वीर भेजें"}
    strings_tr = {"_cls_doc": "Anime kedi kız resmi gönderir"}

    @loader.command(
        ru_doc="[nsfw] - Показать кошкодевочку",
        de_doc="[nsfw] - Zeigt ein Anime-Katzenmädchen-Bild",
        uz_doc="[nsfw] - Anime qiz rasmlarini ko'rsatadi",
        hi_doc="[nsfw] - एक एनीमे कैटगर्ल तस्वीर दिखाएं",
        tr_doc="[nsfw] - Anime kedi kız resmi gönderir",
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
