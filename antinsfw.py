"""
    Copyright 2021 t.me/hikariakami
    Licensed under the Apache License, Version 2.0
    
    Author is not responsible for any consequencies caused by using this
    software or any of its parts. If you have any questions or wishes, feel
    free to contact Dan by sending pm to @hikari_alt.
"""

# <3 title: AntiNSFW
# <3 pic: https://img.icons8.com/fluency/48/000000/change-user-male.png
# <3 desc: NoDesc

from .. import loader, utils
import io
import requests

@loader.tds
class AntiNSFWMod(loader.Module):
    """AntiNSFW"""
    strings = {
        'name': 'AntiNSFW'
    }

    async def client_ready(self, client, db):
        self.db = db
        self.client = client


    async def watcher(self, message):
        if not message.media: return
        # if not message: return
        photo = io.BytesIO()
        await self.client.download_media(message.media, photo)
        photo.seek(0)
        response = requests.post('https://api.hikariakami.ru/check_nsfw', files={'file': photo}, headers={'Authorization': 'Bearer nekoboy_9ci7jg4vqvmx9km7233hsktaq9kur4vz'})
        await utils.answer(message, response.text)
