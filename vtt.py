"""
    Copyright 2021 t.me/innocoffee
    Licensed under the Apache License, Version 2.0
    
    Author is not responsible for any consequencies caused by using this
    software or any of its parts. If you have any questions or wishes, feel
    free to contact Dan by sending pm to @innocoffee_alt.
"""


from .. import loader, utils
from telethon import events
from time import time
import os
try:
    import speech_recognition as sr
    from pydub import AudioSegment
except:
    os.popen('python3 -m pip install pydub speech_recognition --upgrade').read()
    import speech_recognition as sr
    from pydub import AudioSegment

import asyncio
# requires: pydub speechrecognition


@loader.tds
class vttMod(loader.Module):
    strings = {"name": "vtt"}

    async def client_ready(self, client, db):
        self.db = db
        self.chats = self.db.get('vtt', 'chats', [])

    async def recognize(self, event):
        msg = await event.reply('<code>🗣 Проверяю наличие голосового сообщения...</code>')
        try:
            filename = "/tmp/" + str(time()).replace('.', '')
            await event.download_media(file=filename + '.ogg')
            song = AudioSegment.from_ogg(filename + '.ogg')
            song.export(filename + '.wav', format="wav")
            await utils.answer(msg, '<code>🗣 Распознаю голосовое сообщение...</code>')
            r = sr.Recognizer()
            with sr.AudioFile(filename + '.wav') as source:
                audio_data = r.record(source)
                text = r.recognize_google(audio_data, language='ru-RU')
                await utils.answer(msg, '<b>👆 Текст этого войса:</b>\n<pre>' + text + '</pre>')
        except Exception as e:
            if 'ffprobe' in str(e):
                await utils.answer(msg, '<b>Вам необходимо установить ffmpeg.</b> <a href="https://t.me/ftgchatru/454189">Инструкция</a>')
            else:
                await msg.delete()

    @loader.owner
    async def voicycmd(self, message):
        reply = await message.get_reply_message()
        if not reply or not reply.media or not reply.media.document.attributes[0].voice:
            await utils.answer(message, '🗣 <b>Войс не найден</b>')
            await asyncio.sleep(2)
            await message.delete()
            return

        await self.recognize(reply)
        await message.delete()

    @loader.owner
    async def watcher(self, event):
        chat_id = utils.get_chat_id(event)
        if chat_id not in self.chats:
            return

        try:
            if not event.media or not event.media.document.attributes[0].voice:
                return
        except:
            return

        await self.recognize(event)

    async def autovoicecmd(self, message):
        """.autovoice - Напиши это в чате, чтобы автоматически распознавать в нем голосовые. Если написать ее повторно, распознавание будет отключено."""
        chat_id = utils.get_chat_id(message)
        if chat_id in self.chats:
            self.chats.remove(chat_id)
            await utils.answer(message, "<b>🗣 Я больше не буду автоматически распознавать голосовые сообщения в этом чате</b>")
        else:
            self.chats.append(chat_id)
            await utils.answer(message, "<b>🗣 Теперь я буду распознавать голосовые сообщения в этом чате</b>")

        self.db.set('vtt', 'chats', self.chats)
