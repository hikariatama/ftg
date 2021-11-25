"""
    Copyright 2021 t.me/innocoffee
    Licensed under the Apache License, Version 2.0
    
    Author is not responsible for any consequencies caused by using this
    software or any of its parts. If you have any questions or wishes, feel
    free to contact Dan by sending pm to @innocoffee_alt.
"""

# <3 title: Purr
# <3 pic: https://img.icons8.com/fluency/48/000000/cat-head.png
# <3 desc: Отправляет голосовое сообщение с мурчанием

from .. import loader, utils
import requests
import random
import io
import struct
from pydub import AudioSegment


@loader.tds
class KeywordMod(loader.Module):
    """Purr-r-r-r"""
    strings = {
        'name': 'Purr'
    }

    async def client_ready(self, client, db):
        self.db = db
        self.client = client

    @loader.unrestricted
    async def purrcmd(self, message):
        """Sends 'purr' voice message"""
        purrs = [
            'https://x0.at/KFx1.mp3',
            'https://x0.at/jsMN.mp3',
            'https://x0.at/M7ne.mp3',
            'https://x0.at/vB7r.mp3',
            'https://x0.at/RePK.mp3',
            'https://x0.at/7ZEI.mp3'
        ]

        voice = (await utils.run_sync(requests.get, random.choice(purrs))).content

        byte = io.BytesIO(b'0')
        segm = AudioSegment.from_file(io.BytesIO(voice))
        random_duration = random.randint(5000, 15000)
        end = len(segm)-random_duration
        end = len(segm) if end < 0 else end
        random_begin = random.randint(0, end)
        random_begin = 0 if end < 0 else random_begin
        segm[random_begin:min(len(segm), random_begin + random_duration)].export(byte, format="ogg")
        byte.name = 'purr.ogg'
        await self.client.send_file(message.peer_id, byte, caption="<i>🐈 Prrr-r-r-r...</i>", voice_note=True, reply_to=message.reply_to_msg_id)
        await message.delete()
