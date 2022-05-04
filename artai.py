__version__ = (1, 0, 1)

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
# meta developer: @hikariatama
# scope: hikka_only

from .. import loader, utils
from telethon.tl.types import Message
import logging
import requests
import random
import base64
from typing import Union
import asyncio
import io
from ..inline.types import InlineCall

logger = logging.getLogger(__name__)


def base(bytes_: bytes) -> str:
    return f"data:image/jpeg;base64,{base64.b64encode(bytes_).decode()}"


async def animefy(image: bytes, engine: str) -> Union[bytes, bool]:
    answ = await utils.run_sync(
        requests.post,
        "https://hf.space/embed/akhaliq/JoJoGAN/api/queue/push/",
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
            "action": "predict",
        },
    )

    hash_ = answ.json()["hash"]

    status = "WAIT"
    while True:
        ans = (
            await utils.run_sync(
                requests.post,
                "https://hf.space/embed/akhaliq/JoJoGAN/api/queue/status/",
                json={"hash": hash_},
            )
        ).json()
        status = ans["status"]
        logger.debug(ans)

        if status in {"COMPLETE", "FAILED"}:
            break

        yield status
        await asyncio.sleep(2)

    if status == "COMPLETE":
        raw = base64.decodebytes(ans["data"]["data"][0].split("base64,")[1].encode())
        file = io.BytesIO(raw)
        file.name = "photo.jpg"
        yield file
        return

    logger.error(answ.text)

    yield "FAILED"
    return


@loader.tds
class ArtAIMod(loader.Module):
    """Ultimate module, which uses AI to draw ppl"""

    strings = {
        "name": "ArtAI",
        "no_reply": "🚫 <b>Reply to a photo required</b>",
        "pick_engine": "👩‍🎤 <b>Please, choose engine to process this photo</b>",
        "processing": "⌚️ <b>Processing...</b>",
        "downloading": "⬇️ <b>Downloading...</b>",
        "uploading": "☁️ <b>Uploading...</b>",
        "failed": "🚫 <b>Failed</b>",
        "success": (
            "🎨 <b>This is nice</b>|"
            "🎨 <b>Shee-e-esh</b>|"
            "🎨 <b>I'm the artist, this is my POV!</b>|"
            "🎨 <b>Do not blame me, I'm the artist</b>"
        ),
        "queued": "🚽 <b>Waiting in queue...</b>",
    }

    async def client_ready(self, client, db):
        self._db = db
        self._client = client

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
            async for status in animefy(media, engine):
                if status == "QUEUED":
                    await call.edit(self.strings("queued"))
                elif status == "PENDING":
                    await call.edit(self.strings("processing"))
                elif status == "FAILED":
                    await call.edit(self.strings("failed"))
                    return
                else:
                    await call.delete()
                    await self._client.send_file(
                        chat_id,
                        file=status,
                        reply_to=message_id,
                        caption=random.choice(self.strings("success").split("|")),
                    )
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
                suffix = lambda: f" | <i>Engine: {engine}</i>\n\n{''.join(statuses.values())}"  # noqa: E731
                async for status in animefy(media, engine):
                    if status == "QUEUED":
                        await call.edit(self.strings("queued") + suffix())
                        statuses[engine] = "🟨"
                    elif status == "PENDING":
                        await call.edit(self.strings("processing") + suffix())
                        statuses[engine] = "🟦"
                    elif status == "FAILED":
                        await call.edit(self.strings("failed") + suffix())
                        statuses[engine] = "🟥"
                        break
                    else:
                        statuses[engine] = "🟩"
                        res += [status]
                        break

            await call.delete()
            await self._client.send_file(
                chat_id,
                file=res,
                reply_to=message_id,
                caption=random.choice(self.strings("success").split("|")),
            )

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
