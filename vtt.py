# █ █ ▀ █▄▀ ▄▀█ █▀█ ▀    ▄▀█ ▀█▀ ▄▀█ █▀▄▀█ ▄▀█
# █▀█ █ █ █ █▀█ █▀▄ █ ▄  █▀█  █  █▀█ █ ▀ █ █▀█
#
#              © Copyright 2022
#
#          https://t.me/hikariatama
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://img.icons8.com/stickers/500/000000/voice-id.png
# meta developer: @hikariatama
# scope: ffmpeg
# scope: hikka_only
# requires: pydub speechrecognition python-ffmpeg

import asyncio
from time import time

import speech_recognition as sr
from pydub import AudioSegment
from telethon.tl.types import Message

from .. import loader, utils


@loader.tds
class VoicyMod(loader.Module):
    """Recognize voice messages"""

    strings = {
        "name": "Voicy",
        "converting": "<code>🗣 Listening...</code>",
        "converted": "<b>👆 Recognized:</b>\n<pre>{}</pre>",
        "no_ffmpeg": '<b>Install ffmpeg.</b> <a href="https://t.me/ftgchatru/454189">Guide for Heroku</a>',
        "voice_not_found": "🗣 <b>Voice not found</b>",
        "autovoice_off": "<b>🗣 I will not recognize voice messages in this chat</b>",
        "autovoice_on": "<b>🗣 I will recognize voice messages in this chat</b>",
    }

    strings_ru = {
        "converting": "<code>🗣 Распознаю...</code>",
        "converted": "<b>👆 Распознано:</b>\n<pre>{}</pre>",
        "voice_not_found": "🗣 <b>Нет ответа на войс</b>",
        "autovoice_off": "<b>🗣 Я больше не буду распознавать голосовые сообщения в этом чате</b>",
        "autovoice_on": "<b>🗣 Я буду распознавать голосовые сообщения в этом чате</b>",
        "_cmd_doc_voicy": "Распознает голосовое сообщение",
        "_cmd_doc_autovoice": "Включить\\выключить автораспознавание голосовых сообщений в чате",
        "_cls_doc": "Распознает войсы",
    }

    async def client_ready(self, client, db):
        self.chats = self.get("chats", [])

    async def recognize(self, event):
        try:
            filename = "/tmp/" + str(time()).replace(".", "")
            await event.download_media(file=f"{filename}.ogg")
            song = AudioSegment.from_ogg(f"{filename}.ogg")
            song.export(f"{filename}.wav", format="wav")
            event = await utils.answer(event, self.strings("converting"))

            if isinstance(event, (list, set, tuple)):
                event = event[0]

            r = sr.Recognizer()
            with sr.AudioFile(f"{filename}.wav") as source:
                audio_data = r.record(source)
                text = r.recognize_google(audio_data, language="ru-RU")
                await utils.answer(event, self.strings("converted").format(text))
        except Exception as e:
            if "ffprobe" in str(e):
                await utils.answer(event, self.strings("no_ffmpeg"))
                return

            raise

    @loader.unrestricted
    async def voicycmd(self, message: Message):
        """Recognize voice message"""
        reply = await message.get_reply_message()
        if not reply or not reply.media or not reply.media.document.attributes[0].voice:
            await utils.answer(message, self.strings("voice_not_found"))
            await asyncio.sleep(2)
            await message.delete()
            return

        await self.recognize(reply)
        if message.out:
            await message.delete()

    async def watcher(self, event):
        chat_id = utils.get_chat_id(event)

        if chat_id not in self.chats:
            return

        try:
            if not event.media or not event.media.document.attributes[0].voice:
                return
        except Exception:
            return

        await self.recognize(event)

    async def autovoicecmd(self, message: Message):
        """Toggle automatic recognition in current chat"""
        chat_id = utils.get_chat_id(message)
        if chat_id in self.chats:
            self.chats.remove(chat_id)
            await utils.answer(message, self.strings("autovoice_off"))
        else:
            self.chats += [chat_id]
            await utils.answer(message, self.strings("autovoice_on"))

        self.set("chats", self.chats)
