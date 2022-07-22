# scope: hikka_min 1.2.10
__version__ = (2, 0, 0)

#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://img.icons8.com/stickers/500/000000/voice-id.png
# meta banner: https://mods.hikariatama.ru/badges/vtt.jpg
# meta developer: @hikarimods
# scope: ffmpeg
# scope: hikka_only
# requires: pydub speechrecognition python-ffmpeg

import tempfile
import os

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
        "voice_not_found": "🗣 <b>Voice not found</b>",
        "autovoice_off": "<b>🗣 I will not recognize voice messages in this chat</b>",
        "autovoice_on": "<b>🗣 I will recognize voice messages in this chat</b>",
        "_cfg_lang": "Language of voices to recognize",
    }

    strings_ru = {
        "converting": "<code>🗣 Распознаю...</code>",
        "converted": "<b>👆 Распознано:</b>\n<pre>{}</pre>",
        "voice_not_found": "🗣 <b>Нет ответа на войс</b>",
        "autovoice_off": (
            "<b>🗣 Я больше не буду распознавать голосовые сообщения в этом чате</b>"
        ),
        "autovoice_on": "<b>🗣 Я буду распознавать голосовые сообщения в этом чате</b>",
        "_cmd_doc_voicy": "Распознает голосовое сообщение",
        "_cmd_doc_autovoice": (
            "Включить\\выключить автораспознавание голосовых сообщений в чате"
        ),
        "_cls_doc": "Распознает войсы",
        "_cfg_lang": "Язык для распознавания голосовых сообщений",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue("language", "ru-RU", lambda: self.strings("_cfg_lang"))
        )

    async def recognize(self, message: Message):
        with tempfile.TemporaryDirectory() as tmpdir:
            file = os.path.join(tmpdir, "audio.ogg")

            with open(file, "wb") as f:
                f.write(await message.download_media(bytes))

            song = AudioSegment.from_ogg(file)
            song.export(os.path.join(tmpdir, "audio.wav"), format="wav")
            message = await utils.answer(message, self.strings("converting"))

            r = sr.Recognizer()

            with sr.AudioFile(os.path.join(tmpdir, "audio.wav")) as source:
                audio_data = r.record(source)
                text = r.recognize_google(audio_data, language=self.config["language"])
                await utils.answer(message, self.strings("converted").format(text))

    @loader.unrestricted
    async def voicycmd(self, message: Message):
        """Recognize voice message"""
        reply = await message.get_reply_message()
        try:
            is_voice = reply.media.document.attributes[0].voice
        except (AttributeError, IndexError):
            is_voice = False

        if not reply or not reply.media or not is_voice:
            await utils.answer(message, self.strings("voice_not_found"))
            return

        await self.recognize(reply)

        if message.out:
            await message.delete()

    async def watcher(self, message: Message):
        try:
            if (
                utils.get_chat_id(message) not in self.get("chats", [])
                or not message.media
                or not message.media.document.attributes[0].voice
            ):
                return
        except Exception:
            return

        await self.recognize(message)

    async def autovoicecmd(self, message: Message):
        """Toggle automatic recognition in current chat"""
        chat_id = utils.get_chat_id(message)

        if chat_id in self.get("chats", []):
            self.set("chats", list(set(self.get("chats", [])) - {chat_id}))
            await utils.answer(message, self.strings("autovoice_off"))
        else:
            self.set("chats", self.get("chats", []) + [chat_id])
            await utils.answer(message, self.strings("autovoice_on"))
