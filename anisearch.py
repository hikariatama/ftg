#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# scope: hikka_min 1.2.10

# meta pic: https://img.icons8.com/external-flatart-icons-flat-flatarticons/512/000000/external-frame-valentines-day-flatart-icons-flat-flatarticons-1.png
# meta developer: @hikarimods

import requests
from telethon.tl.types import Message

from .. import loader, utils


@loader.tds
class AniSearchMod(loader.Module):
    """Searches for anime exact moment by only frame screenshot"""

    strings = {
        "name": "AniSearch",
        "404": "😶‍🌫️ <b>I don't know which anime it is...</b>",
        "searching": "🐵 <b>Let me take a look...</b>",
        "result": (
            "😎 <b>I think, it is... </b><code>{}</code><b> episode"
            " </b><code>{}</code><b> at</b> <code>{}</code>\n<b>I'm sure at {}%</b>"
        ),
        "media_not_found": "🚫 <b>Media not found</b>",
    }

    strings_ru = {
        "404": "😶‍🌫️ <b>Я не знаю, что это за аниме...</b>",
        "searching": "🐵 <b>Дай глянуть...</b>",
        "result": (
            "😎 <b>Я думаю, что это... </b><code>{}</code><b> эпизод"
            " </b><code>{}</code><b> на</b> <code>{}</code>\n<b>Я уверен на {}%</b>"
        ),
        "media_not_found": "🚫 <b>Медиа не найдено</b>",
        "_cmd_doc_anisearch": "Поиск аниме по скриншоту",
        "_cls_doc": "Ищет конкретную серию и тайм-код аниме по скриншоту",
    }

    async def anisearchcmd(self, message: Message):
        """Search anime by frame"""
        reply = await message.get_reply_message()
        if not message.media and (not reply or not reply.media):
            await utils.answer(message, self.strings("media_not_found"))
            return

        message = await utils.answer(message, self.strings("searching"))
        search_result = requests.post(
            "https://api.trace.moe/search",
            files={
                "image": await self._client.download_media(
                    message if message.media else reply,
                    bytes,
                )
            },
        ).json()

        if not search_result or not search_result.get("result", False):
            await utils.answer(message, self.strings("404"))
            return

        anilist = requests.post(
            "https://graphql.anilist.co",
            json={
                "query": (
                    "query($id: Int) {Media(id: $id, type: ANIME) {id idMal title"
                    " {native romaji english } synonyms isAdult } }"
                ),
                "variables": {"id": search_result["result"][0]["anilist"]},
            },
        ).json()

        title = (
            anilist["data"]["Media"]["title"]["english"]
            or anilist["data"]["Media"]["title"]["romaji"]
            or anilist["data"]["Media"]["title"]["native"]
        )

        if not title:
            await utils.answer(message, self.strings("media_not_found"))
            return

        pos = search_result["result"][0]["from"]
        episode = search_result["result"][0]["episode"]
        conf = search_result["result"][0]["similarity"]

        await utils.answer(
            message,
            self.strings("result").format(
                title,
                episode,
                f"{round(pos // 60)}:{round(pos % 60)}",
                round(conf * 100, 2),
            ),
        )
