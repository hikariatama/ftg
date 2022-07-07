__version__ = (1, 0, 2)

# █ █ ▀ █▄▀ ▄▀█ █▀█ ▀    ▄▀█ ▀█▀ ▄▀█ █▀▄▀█ ▄▀█
# █▀█ █ █ █ █▀█ █▀▄ █ ▄  █▀█  █  █▀█ █ ▀ █ █▀█
#
#              © Copyright 2022
#
#          https://t.me/hikariatama
#
# 🔒 Licensed under the CC BY-NC-ND 4.0
# 🌐 https://creativecommons.org/licenses/by-nc-nd/4.0

# meta pic: https://img.icons8.com/fluency/240/000000/class-dojo.png
# meta developer: @hikarimods
# scope: hikka_only

import asyncio
import base64
import io
import logging
import random
from typing import Union

import requests
from telethon.tl.types import Message

from .. import loader, utils
from ..inline.types import InlineCall

logger = logging.getLogger(__name__)


def base(bytes_: bytes) -> str:
    return f"data:image/jpeg;base64,{base64.b64encode(bytes_).decode()}"


async def animefy(image: bytes, engine: str) -> Union[bytes, bool]:
    answ = await utils.run_sync(
        requests.post,
        "https://hf.space/embed/akhaliq/JoJoGAN/api/predict/",
        headers={
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-US,en;q=0.9",
            "connection": "keep-alive",
            "content-length": "58501",
            "content-type": "application/json",
            "host": "hf.space",
            "origin": "https://hf.space",
            "referer": "https://hf.space/embed/akhaliq/JoJoGAN/+",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "sec-gpc": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36",
        },
        json={
            "data": [base(image), engine],
            "example_id": None,
            "session_hash": "".join(
                [
                    random.choice("abcdefghijklmnopqrstuvwxyz1234567890")
                    for _ in range(11)
                ]
            ),
        },
    )

    file = io.BytesIO(
        base64.decodebytes(answ.json()["data"][0].split("base64,")[1].encode())
    )
    file.name = "photo.jpg"
    return file


@loader.tds
class ArtAIMod(loader.Module):
    """Ultimate module, which uses AI to draw ppl"""

    strings = {
        "name": "ArtAI",
        "no_reply": "🚫 <b>Reply to a photo required</b>",
        "pick_engine": "👩‍🎤 <b>Please, choose engine to process this photo</b>",
        "uploading": "☁️ <b>Uploading...</b>",
        "success": (
            "🎨 <b>This is nice</b>|"
            "🎨 <b>Shee-e-esh</b>|"
            "🎨 <b>I'm the artist, this is my POV!</b>|"
            "🎨 <b>Do not blame me, I'm the artist</b>"
        ),
    }

    async def on_unload(self):
        asyncio.ensure_future(
            self._client.inline_query("@hikkamods_bot", "#statunload:artai")
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

        self.allmodules._hikari_stats += ["artai"]

        if not hasattr(self.allmodules, "_hikari_stats_task"):
            self.allmodules._hikari_stats_task = asyncio.ensure_future(
                self.stats_task()
            )

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
                caption=random.choice(self.strings("success").split("|")),
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
                    lambda: f"<i>Processing image...</i>\n\n{''.join(statuses.values())}"
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
                    caption=random.choice(self.strings("success").split("|")),
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
