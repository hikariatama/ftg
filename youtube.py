"""
    Copyright 2021 t.me/hikariatama
    Licensed under the Apache License, Version 2.0
    
    Author is not responsible for any consequencies caused by using this
    software or any of its parts. If you have any questions or wishes, feel
    free to contact Dan by sending pm to @hikari_alt.
"""

# <3 title: YouTube
# <3 pic: https://img.icons8.com/fluency/50/000000/youtube.png
# <3 desc: Скачать видео с YouTube

from .. import loader, utils
import requests
import json
from pytube import YouTube
import os
import time
import subprocess
# requires: pytube

@loader.tds
class YouTubeMod(loader.Module):
    """Download YouTube video"""
    strings = {
        'name': 'YouTube',
        'args': '🎞 <b>You need to specify link</b>',
        'downloading': '🎞 <b>Downloading...</b>',
        'not_found': '🎞 <b>Video not found...</b>'
    }

    async def client_ready(self, client, db):
        self.db = db
        self.client = client

    @loader.unrestricted
    async def ytcmd(self, message):
        """[mp3] <link> - Download video from youtube"""
        args = utils.get_args_raw(message)
        message = await utils.answer(message, self.strings('downloading'))
        try:
            message = message[0]
        except: pass
        ext = False
        if len(args.split()) > 1:
            ext, args = args.split(maxsplit=1)

        if not args:
            return await utils.answer(message, self.strings('args'))

        def dlyt(videourl, path):
            yt = YouTube(videourl)
            yt = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
            return yt.download(path)

        def convert_video_to_audio_ffmpeg(video_file, output_ext="mp3"):
            filename, ext = os.path.splitext(video_file)
            out = f"{filename}.{output_ext}"
            subprocess.call(["ffmpeg", "-y", "-i", video_file, out], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            os.remove(video_file)
            return out

        path = '/tmp'
        try:
            path = await utils.run_sync(dlyt, args, path)
        except:
            return await utils.answer(message, self.strings('not_found'))

        if ext == 'mp3':
            path = convert_video_to_audio_ffmpeg(path)

        await self.client.send_file(message.peer_id, path)
        os.remove(path)
        await message.delete()


