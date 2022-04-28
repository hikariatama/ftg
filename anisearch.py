# █ █ ▀ █▄▀ ▄▀█ █▀█ ▀    ▄▀█ ▀█▀ ▄▀█ █▀▄▀█ ▄▀█
# █▀█ █ █ █ █▀█ █▀▄ █ ▄  █▀█  █  █▀█ █ ▀ █ █▀█
#
#              © Copyright 2022
#
#          https://t.me/hikariatama
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://img.icons8.com/color/48/000000/boruto-uzumaki.png
# meta developer: @hikariatama

from .. import loader, utils
from telethon.tl.types import Message
import logging
import requests

logger = logging.getLogger(__name__)


@loader.tds
class AniSearchMod(loader.Module):
    """Searches for anime exact moment by only frame screenshot"""

    strings = {
        "name": "AniSearch",
        "404": "😶‍🌫️ <b>I don't know which anime it is...</b>",
        "searching": "🐵 <b>Let me take a look...</b>",
        "result": "😎 <b>I think, it is... </b><code>{}</code><b> episode </b><code>{}</code><b> at</b> <code>{}</code>\n<b>I'm sure at {}%</b>",
        "media_not_found": "🚫 <b>Media not found</b>",
    }

    async def client_ready(self, client, db):
        self._db = db
        self._client = client

    async def anisearchcmd(self, message: Message):
        """Search anime by frame"""
        reply = await message.get_reply_message()
        if not message.media and (not reply or not reply.media):
            await utils.answer(message, self.strings("media_not_found"))
            return

        message = await utils.answer(message, self.strings("searching"))
        if isinstance(message, (tuple, list, set)):
            message = message[0]

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
                "query": "query($id: Int) {Media(id: $id, type: ANIME) {id idMal title {native romaji english } synonyms isAdult } }",
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
