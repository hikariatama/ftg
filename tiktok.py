"""
    Copyright 2021 t.me/hikariakami
    Licensed under the Apache License, Version 2.0
    
    Author is not responsible for any consequencies caused by using this
    software or any of its parts. If you have any questions or wishes, feel
    free to contact Dan by sending pm to @hikari_alt.
"""

#<3 title: TikTok
#<3 pic: https://img.icons8.com/fluency/48/000000/tiktok.png
#<3 desc: Скачивает видосы TikTok nwm

from .. import loader, utils
import asyncio
import requests

class TikTokMod(loader.Module):
    """Download TikTok video w\\o watermark"""
    strings = {'name': 'TikTok', 
    'loading': "<b>🦊 Download in progress...</b>", 
    'no_link': "<b>🦊 No link specified!</b>"}

    async def client_ready(self, client, db):
        self.client = client

    @loader.unrestricted
    async def ttcmd(self, message):
        """<link> - Download TikTok video nwm"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings('no_link', message))
            await asyncio.sleep(3)
            await message.delete()
            return

        message = await utils.answer(message, self.strings('loading', message))
        try:
            message = message[0]
        except: pass

        ans = requests.get('https://snaptik.cc').text

        def trim(string, f, t):
            begin = string.find(f) + len(f)
            return string[begin:string.find('"', begin)]

        token = trim(ans, '="_token_" content="', '"')
        res = requests.get(f'https://snaptik.cc/api/v1/fetch?url={args}', headers={'token': token}).json()

        await self.client.send_file(message.peer_id, res['url_nwm'])
        await message.delete()

