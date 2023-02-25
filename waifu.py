#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://static.hikari.gay/waifu_icon.png
# meta banner: https://mods.hikariatama.ru/badges/waifu.jpg
# meta developer: @hikarimods
# scope: inline
# scope: hikka_only
# scope: hikka_min 1.2.10

import functools
import logging

import requests
from telethon.tl.types import Message

from .. import loader, utils

logger = logging.getLogger(__name__)
categories = [
    "waifu",
    "neko",
    "shinobu",
    "megumin",
    "cuddle",
    "cry",
    "hug",
    "awoo",
    "kiss",
    "lick",
    "pat",
    "smug",
    "bonk",
    "yeet",
    "blush",
    "smile",
    "wave",
    "highfive",
    "handhold",
    "nom",
    "bite",
    "glomp",
    "slap",
]
nsfw_categories = ["waifu", "neko", "trap", "blowjob"]


async def photo(type_: str, category: str) -> list:
    if category in nsfw_categories and category not in categories:
        type_ = "nsfw"

    ans = (
        await utils.run_sync(
            requests.post,
            f"https://api.waifu.pics/many/{type_}/{category}",
            json={"exclude": []},
        )
    ).json()

    if "files" not in ans:
        logger.error(ans)
        return []

    return ans["files"]


@loader.tds
class WaifuMod(loader.Module):
    """Unleash best waifus of all time"""

    strings = {"name": "Waifu"}

    async def waifucmd(self, message: Message):
        """[nsfw] [category] - Send waifu"""
        category = (
            [
                category
                for category in categories + nsfw_categories
                if category in utils.get_args_raw(message)
            ]
            or [
                (
                    categories[0]
                    if "nsfw" not in utils.get_args_raw(message)
                    else nsfw_categories[0]
                )
            ]
        )[0]

        await self.inline.gallery(
            message=message,
            next_handler=functools.partial(
                photo,
                type_=("nsfw" if "nsfw" in utils.get_args_raw(message) else "sfw"),
                category=category,
            ),
            caption=(
                f"<b>{('🔞 NSFW' if 'nsfw' in utils.get_args_raw(message) else '👨‍👩‍👧 SFW')}</b>:"
                f" <i>{category}</i>"
            ),
            preload=10,
        )

    async def waifuscmd(self, message: Message):
        """Show available categories"""
        await utils.answer(
            message,
            "\n".join(
                [
                    " | ".join(i)
                    for i in utils.chunks([f"<code>{i}</code>" for i in categories], 5)
                ]
            )
            + "\n<b>NSFW:</b>\n"
            + "\n".join(
                [
                    " | ".join(i)
                    for i in utils.chunks(
                        [f"<code>{i}</code>" for i in nsfw_categories], 5
                    )
                ]
            ),
        )
