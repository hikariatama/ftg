__version__ = (1, 1, 0)

#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#
#          https://t.me/hikariatama
#
# 🔒 Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://static.dan.tatar/artai_icon.png
# meta banner: https://mods.hikariatama.ru/badges/artai.jpg
# meta developer: @hikarimods
# scope: hikka_only
# scope: hikka_min 1.2.10

import asyncio
import base64
import io
import random
from typing import Union

import requests
from telethon.tl.types import Message

from .. import loader, utils
from ..inline.types import InlineCall


def base(bytes_: bytes) -> str:
    return f"data:image/jpeg;base64,{base64.b64encode(bytes_).decode()}"


async def poll(queue_hash: str) -> str:
    for _ in range(50):
        answ = await utils.run_sync(
            requests.post,
            "https://akhaliq-jojogan.hf.space/api/queue/status/",
            params={"hash": queue_hash},
        )

        if answ.json()["status"] == "COMPLETE":
            return answ.json()["data"]["data"][0]
        elif answ.json()["status"] != "PENDING":
            return False

        await asyncio.sleep(3)


async def animefy(image: bytes, engine: str) -> Union[bytes, bool]:
    file = io.BytesIO(
        base64.decodebytes(
            (
                await poll(
                    (
                        await utils.run_sync(
                            requests.post,
                            "https://akhaliq-jojogan.hf.space/api/queue/push/",
                            headers={
                                "accept": "*/*",
                                "accept-encoding": "gzip, deflate, br",
                                "accept-language": "en-US,en;q=0.9,ru;q=0.8",
                                "cache-control": "no-cache",
                                "content-type": "application/json",
                                "origin": "https://akhaliq-jojogan.hf.space",
                                "pragma": "no-cache",
                                "referer": (
                                    "https://akhaliq-jojogan.hf.space/?__theme=light"
                                ),
                                "sec-fetch-dest": "empty",
                                "sec-fetch-mode": "cors",
                                "sec-fetch-site": "same-origin",
                                "sec-gpc": "1",
                                "user-agent": (
                                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                                    " AppleWebKit/537.36 (KHTML, like Gecko)"
                                    " Chrome/92.0.4515.131 Safari/537.36"
                                ),
                            },
                            json={
                                "action": "predict",
                                "data": [base(image), engine],
                                "fn_index": 0,
                                "session_hash": utils.rand(11).lower(),
                            },
                        )
                    ).json()["hash"]
                )
            )
            .split("base64,")[1]
            .encode()
        )
    )
    file.name = "photo.jpg"
    return file


@loader.tds
class ArtAIMod(loader.Module):
    """Ultimate module, which uses AI to draw ppl"""

    paint = "<emoji document_id=5431456208487716895>🎨</emoji>"

    strings = {
        "name": "ArtAI",
        "no_reply": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Reply to a photo"
            " required</b>"
        ),
        "pick_engine": "👩‍🎤 <b>Please, choose engine to process this photo</b>",
        "uploading": "☁️ <b>Uploading...</b>",
        "success": (
            f"{paint} <b>This is nice</b>",
            f"{paint} <b>Shee-e-esh</b>",
            f"{paint} <b>I'm the artist, this is my POV!</b>",
            f"{paint} <b>Do not blame me, I'm the artist</b>",
        ),
    }

    strings_ru = {
        "no_reply": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Ответь на фото</b>"
        ),
        "pick_engine": "👩‍🎤 <b>Выбери движок для обработки этой фотографии</b>",
        "uploading": "☁️ <b>Загружаю...</b>",
        "success": (
            f"{paint} <b>Это классно</b>",
            f"{paint} <b>Shee-e-esh</b>",
            f"{paint} <b>Я художник, я так вижу!</b>",
            f"{paint} <b>Не обвиняй меня, я художник</b>",
        ),
    }

    strings_de = {
        "no_reply": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Antworte auf ein"
            " Foto</b>"
        ),
        "pick_engine": "👩‍🎤 <b>Wähle einen Motor, um dieses Foto zu verarbeiten</b>",
        "uploading": "☁️ <b>Hochladen...</b>",
        "success": (
            f"{paint} <b>Das ist schön</b>",
            f"{paint} <b>Shee-e-esh</b>",
            f"{paint} <b>Ich bin der Künstler, das ist meine Sicht!</b>",
            f"{paint} <b>Verurteile mich nicht, ich bin der Künstler</b>",
        ),
    }

    strings_uz = {
        "no_reply": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Fotoya javob"
            " bering</b>"
        ),
        "pick_engine": "👩‍🎤 <b>Ushbu rasmni ishlash uchun injinani tanlang</b>",
        "uploading": "☁️ <b>Yuklanmoqda...</b>",
        "success": (
            f"{paint} <b>Bu yaxshi</b>",
            f"{paint} <b>Shee-e-esh</b>",
        ),
    }

    strings_es = {
        "no_reply": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Responde a una"
            " foto</b>"
        ),
        "pick_engine": "👩‍🎤 <b>Elige un motor para procesar esta foto</b>",
        "uploading": "☁️ <b>Subiendo...</b>",
        "success": (
            f"{paint} <b>Esto es bueno</b>",
            f"{paint} <b>Shee-e-esh</b>",
            f"{paint} <b>Soy el artista, esta es mi visión</b>",
            f"{paint} <b>No me culpes, soy el artista</b>",
        ),
    }

    strings_tr = {
        "no_reply": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Bir fotoğrafa yanıt"
            " verin</b>"
        ),
        "pick_engine": "👩‍🎤 <b>Bu fotoğrafı işlemek için bir motor seçin</b>",
        "uploading": "☁️ <b>Yükleniyor...</b>",
        "success": (
            f"{paint} <b>Bu güzel</b>",
            f"{paint} <b>Shee-e-esh</b>",
            f"{paint} <b>Ben sanatçıyım, bu benim bakış açım!</b>",
            f"{paint} <b>Sana suçlamayın, ben sanatçıyım</b>",
        ),
    }

    async def artaicmd(self, message: Message):
        """<photo> - Create anime art from photo"""
        reply = await message.get_reply_message()

        if not reply or not reply.photo:
            await utils.answer(message, self.strings("no_reply"))
            return

        await self.inline.form(
            message=message,
            text=self.strings("pick_engine"),
            reply_markup=self._gen_markup(reply),
        )

    async def _process_engine(
        self,
        call: InlineCall,
        engine: str,
        chat_id: int,
        message_id: int,
    ):
        await call.edit(self.strings("uploading"))
        media = await self._client.download_media(
            (
                await self._client.get_messages(
                    entity=chat_id,
                    ids=[message_id],
                    limit=1,
                )
            )[0],
            bytes,
        )

        if engine != "All":
            await self._client.send_file(
                chat_id,
                file=await animefy(media, engine),
                reply_to=message_id,
                caption=random.choice(self.strings("success")),
            )
            await call.delete()
            return
        else:
            res = []

            statuses = {
                "JoJo": "⬜️",
                "Disney": "⬜️",
                "Jinx": "⬜️",
                "Caitlyn": "⬜️",
                "Yasuho": "⬜️",
                "Arcane Multi": "⬜️",
                "Art": "⬜️",
                "Spider-Verse": "⬜️",
                "Sketch": "⬜️",
            }

            for engine in statuses:
                suffix = (
                    lambda: (
                        f"<i>Processing image...</i>\n\n{''.join(statuses.values())}"
                    )
                )
                res += [await animefy(media, engine)]
                statuses[engine] = "🟩"
                await call.edit(suffix())

            await call.delete()
            try:
                await self._client.send_file(
                    chat_id,
                    file=res,
                    reply_to=message_id,
                    caption=random.choice(self.strings("success")),
                )
            except TypeError:
                pass

    def _gen_markup(self, reply: Message) -> list:
        engines = [
            "👊 JoJo",
            "👸 Disney",
            "🥷 Jinx",
            "😥 Caitlyn",
            "👩‍🎤 Yasuho",
            "👨‍🎤 Arcane Multi",
            "🎨 Art",
            "🕸 Spider-Verse",
            "✒️ Sketch",
            "🎁 All",
        ]

        return utils.chunks(
            [
                {
                    "text": engine,
                    "callback": self._process_engine,
                    "args": (
                        engine.split(maxsplit=1)[1],
                        utils.get_chat_id(reply),
                        reply.id,
                    ),
                }
                for engine in engines
            ],
            2,
        )
