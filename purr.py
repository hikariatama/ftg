#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html


# meta pic: https://static.hikari.gay/purr_icon.png
# meta banner: https://mods.hikariatama.ru/badges/purr.jpg
# requires: pydub python-ffmpeg
# meta developer: @hikarimods
# scope: ffmpeg
# scope: hikka_only
# scope: hikka_min 1.2.10

import io
import random

import requests
from pydub import AudioSegment
from telethon.tl.types import Message

from .. import loader, utils


@loader.tds
class KeywordMod(loader.Module):
    """Sends purr-r message"""

    strings = {"name": "Purr"}

    @loader.unrestricted
    async def purrcmd(self, message: Message):
        """Sends 'purr' voice message"""
        args = utils.get_args_raw(message) or "<i>🐈 Purrr-r-r-r...</i>"
        purrs = [
            "https://github.com/hikariatama/assets/raw/master/ne6O.mp3",
            "https://github.com/hikariatama/assets/raw/master/Kc0L.mp3",
            "https://github.com/hikariatama/assets/raw/master/rGdI.mp3",
            "https://github.com/hikariatama/assets/raw/master/3mtz.mp3",
            "https://github.com/hikariatama/assets/raw/master/3U9J.mp3",
        ]

        voice = (await utils.run_sync(requests.get, random.choice(purrs))).content

        byte = io.BytesIO(b"0")
        segm = AudioSegment.from_file(io.BytesIO(voice))
        random_duration = random.randint(5000, 15000)
        end = len(segm) - random_duration
        end = len(segm) if end < 0 else end
        random_begin = random.randint(0, end)
        random_begin = 0 if end < 0 else random_begin

        segm[random_begin : min(len(segm), random_begin + random_duration)].export(
            byte,
            format="ogg",
        )

        byte.name = "purr.ogg"

        await self._client.send_file(
            message.peer_id,
            byte,
            caption=args,
            voice_note=True,
            reply_to=message.reply_to_msg_id,
        )

        if message.out:
            await message.delete()
