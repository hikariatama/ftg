#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://static.hikari.gay/anisearch_icon.png
# meta banner: https://mods.hikariatama.ru/badges/anisearch.jpg
# meta developer: @hikarimods
# scope: hikka_only
# scope: hikka_min 1.2.10

import requests
from telethon.tl.types import Message

from .. import loader, utils


@loader.tds
class AniSearchMod(loader.Module):
    """Searches for anime exact moment by only frame screenshot"""

    strings = {
        "name": "AniSearch",
        "404": (
            "<emoji document_id=5204174553592372633>😢</emoji> <b>I don't know which"
            " anime it is...</b>"
        ),
        "searching": (
            "<emoji document_id=5424885441100782420>👀</emoji> <b>Let me take a"
            " look...</b>"
        ),
        "result": (
            "<emoji document_id=5312017978349331498>😎</emoji> <b>I think, it is..."
            " </b><code>{}</code><b> episode </b><code>{}</code><b> at</b>"
            " <code>{}</code>\n<b>I'm sure at {}%</b>"
        ),
        "media_not_found": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Media not found</b>"
        ),
    }

    strings_ru = {
        "404": (
            "<emoji document_id=5204174553592372633>😢</emoji> <b>Я не знаю, что это за"
            " аниме...</b>"
        ),
        "searching": (
            "<emoji document_id=5424885441100782420>👀</emoji> <b>Дай глянуть...</b>"
        ),
        "result": (
            "<emoji document_id=5312017978349331498>😎</emoji> <b>Я думаю, что это..."
            " </b><code>{}</code><b> эпизод </b><code>{}</code><b> на</b>"
            " <code>{}</code>\n<b>Я уверен на {}%</b>"
        ),
        "media_not_found": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Медиа не найдено</b>"
        ),
        "_cmd_doc_anisearch": "Поиск аниме по скриншоту",
        "_cls_doc": "Ищет конкретную серию и тайм-код аниме по скриншоту",
    }

    strings_de = {
        "404": (
            "<emoji document_id=5204174553592372633>😢</emoji> <b>Ich weiß nicht,"
            " welcher Anime das ist...</b>"
        ),
        "searching": (
            "<emoji document_id=5424885441100782420>👀</emoji> <b>Lass mich mal"
            " schauen...</b>"
        ),
        "result": (
            "<emoji document_id=5312017978349331498>😎</emoji> <b>Ich denke, es ist..."
            " </b><code>{}</code><b> Folge </b><code>{}</code><b> um</b>"
            " <code>{}</code>\n<b>Ich bin mir zu {}% sicher</b>"
        ),
        "media_not_found": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Medien nicht"
            " gefunden</b>"
        ),
        "_cmd_doc_anisearch": "Suche Anime nach einem Screenshot",
        "_cls_doc": (
            "Sucht nach einer bestimmten Folge und Zeitstempel eines Anime nach einem"
            " Screenshot"
        ),
    }

    strings_hi = {
        "404": (
            "<emoji document_id=5204174553592372633>😢</emoji> <b>मैं नहीं जानता कि यह"
            " कौन सी एनीमे है...</b>"
        ),
        "searching": (
            "<emoji document_id=5424885441100782420>👀</emoji> <b>मुझे देखने के लिए दें...</b>"
        ),
        "result": (
            "<emoji document_id=5312017978349331498>😎</emoji> <b>मैं सोचता हूँ कि..."
            " </b><code>{}</code><b> एपिसोड </b><code>{}</code><b> में</b>"
            " <code>{}</code>\n<b>मैं {}% सुनिश्चित हूँ</b>"
        ),
        "media_not_found": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>मीडिया नहीं मिला</b>"
        ),
        "_cmd_doc_anisearch": "एक स्क्रीनशॉट के लिए एनीमे खोजें",
        "_cls_doc": "एक स्क्रीनशॉट के लिए एक विशिष्ट एपिसोड और समय-स्टैंप खोजता है",
    }

    strings_uz = {
        "404": (
            "<emoji document_id=5204174553592372633>😢</emoji> <b>Bu anime haqida"
            " gapirishim mumkin emas...</b>"
        ),
        "searching": (
            "<emoji document_id=5424885441100782420>👀</emoji> <b>Qarashimni ko'rish"
            " uchun beraman...</b>"
        ),
        "result": (
            "<emoji document_id=5312017978349331498>😎</emoji> <b>Aytaman..."
            " </b><code>{}</code><b>  </b><code>{}</code><b> da</b>"
            " <code>{}</code>\n<b>Menga %{} hisoblanadi</b>"
        ),
        "media_not_found": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Media topilmadi</b>"
        ),
        "_cmd_doc_anisearch": "Ekran rasmini ishlatib anime qidirish",
        "_cls_doc": (
            "Ekran rasmini ishlatib biror animening biror qismi va vaqtini qidiradi"
        ),
    }

    strings_tr = {
        "404": (
            "<emoji document_id=5204174553592372633>😢</emoji> <b>Bu anime hakkında"
            " bilgim yok...</b>"
        ),
        "searching": (
            "<emoji document_id=5424885441100782420>👀</emoji> <b>Göz atayım...</b>"
        ),
        "result": (
            "<emoji document_id=5312017978349331498>😎</emoji> <b>Sanırım..."
            " </b><code>{}</code><b>  </b><code>{}</code><b> da</b>"
            " <code>{}</code>\n<b>%{} ihtimalle</b>"
        ),
        "media_not_found": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Medya bulunamadı</b>"
        ),
        "_cmd_doc_anisearch": "Bir ekran görüntüsü kullanarak anime arama",
        "_cls_doc": (
            "Bir ekran görüntüsü kullanarak bir anime serisinin ve zaman damgasının bir"
            " kısmını arar"
        ),
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
