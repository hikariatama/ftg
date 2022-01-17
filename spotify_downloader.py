"""
    Copyright 2021 t.me/hikariatama
    Licensed under the Apache License, Version 2.0
    
    Author is not responsible for any consequencies caused by using this
    software or any of its parts. If you have any questions or wishes, feel
    free to contact Dan by sending pm to @hikari_alt.
"""

#<3 title: SpotifyDownloader
#<3 pic: https://img.icons8.com/fluency/48/000000/spotify.png
#<3 desc: Скачивает треки из Spotify

from .. import loader, utils

@loader.tds
class SpotifyDownloaderMod(loader.Module):
    """Download music from Spotify"""
    strings = {
        'name': 'SpotifyDownloader'
    }
    
    async def client_ready(self, client, db):
        self.db = db
        self.client = client
    @loader.unrestricted
    async def sdcmd(self, message):
        """<track> - search and download from Spotify"""
        args = utils.get_args_raw(message)
        if not args:
            return await utils.answer(message, "<b>No args.</b>") 

        message = await utils.answer(message, "<b>Loading...</b>")
        try:
            message = message[0]
        except: pass
        music = await self.client.inline_query('spotifysavebot', args)
        for mus in music:
            if mus.result.type == 'audio':
                await self.client.send_file(message.peer_id, mus.result.document, reply_to=message.reply_to_msg_id)
                return await message.delete()

        return await utils.answer(message, f"<b> Music named <code> {args} </code> not found. </b>")  
