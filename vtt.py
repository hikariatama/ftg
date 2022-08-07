__version__ = (2, 0, 0)

#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://static.hikari.gay/vtt_icon.png
# meta banner: https://mods.hikariatama.ru/badges/vtt.jpg
# meta developer: @hikarimods
# scope: ffmpeg
# scope: hikka_only
# scope: hikka_min 1.2.10
# requires: pydub speechrecognition python-ffmpeg

import tempfile
import os
import logging

import speech_recognition as sr
from pydub import AudioSegment
from telethon.tl.types import Message

from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class VoicyMod(loader.Module):
    """Recognize voice messages, audios, videos and round messages"""

    strings = {
        "name": "Voicy",
        "converting": "<b>🫠 Recognizing voice message...</b>",
        "converted": "<b>🫠 Recognized:</b>\n<i>{}</i>",
        "voice_not_found": "🫠 <b>Voice not found</b>",
        "autovoice_off": "<b>🫠 I will not recognize voice messages in this chat</b>",
        "autovoice_on": "<b>🫠 I will recognize voice messages in this chat</b>",
        "_cfg_lang": "Language of voices to recognize",
        "_cfg_engine": "Recognition engine",
        "error": "🚫 <b>Recognition error!</b>",
        "_cfg_ignore_users": "Users to ignore",
    }

    strings_ru = {
        "converting": "<b>🫠 Распознаю голосовое сообщение...</b>",
        "converted": "<b>🫠 Распознано:</b>\n<i>{}</i>",
        "voice_not_found": "🫠 <b>Нет ответа на войс</b>",
        "autovoice_off": (
            "<b>🫠 Я больше не буду распознавать голосовые сообщения в этом чате</b>"
        ),
        "autovoice_on": "<b>🫠 Я буду распознавать голосовые сообщения в этом чате</b>",
        "_cmd_doc_voicy": "Распознает голосовое сообщение",
        "_cmd_doc_autovoice": (
            "Включить\\выключить автораспознавание голосовых сообщений в чате"
        ),
        "_cls_doc": "Распознает голосовые сообщения, аудио, видео и кругляши",
        "_cfg_lang": "Язык для распознавания голосовых сообщений",
        "_cfg_engine": "Распознаватель",
        "_cfg_ignore_users": "Игнорировать пользователей",
        "error": "🚫 <b>Ошибка распознавания!</b>",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "language",
                "ru-RU",
                lambda: self.strings("_cfg_lang"),
                validator=loader.validators.RegExp(r"^[a-z]{2}-[A-Z]{2}$"),
            ),
            loader.ConfigValue(
                "ignore_users",
                [],
                lambda: self.strings("_cfg_ignore_users"),
                validator=loader.validators.Series(validator=loader.validators.TelegramID()),
            )
        )

    async def client_ready(self):
        self.v2a = await self.import_lib(
            "https://libs.hikariatama.ru/v2a.py",
            suspend_on_error=True,
        )

    async def recognize(self, message: Message):
        try:
            message = await utils.answer(message, self.strings("converting"))
            with tempfile.TemporaryDirectory() as tmpdir:
                file = os.path.join(
                    tmpdir,
                    "audio.mp3" if message.audio else "audio.ogg",
                )

                data = await message.download_media(bytes)

                if message.video:
                    data = await self.v2a.convert(data, "audio.ogg")

                with open(file, "wb") as f:
                    f.write(data)

                song = AudioSegment.from_file(file, format="mp3" if message.audio else "ogg")
                song.export(os.path.join(tmpdir, "audio.wav"), format="wav")

                r = sr.Recognizer()

                with sr.AudioFile(os.path.join(tmpdir, "audio.wav")) as source:
                    audio_data = r.record(source)
                    text = await utils.run_sync(
                        r.recognize_google,
                        audio_data,
                        language=self.config["language"],
                    )
                    message = await utils.answer(
                        message,
                        self.strings("converted").format(text),
                    )
        except Exception:
            logger.exception("Can't recognize")
            await utils.answer(message, self.strings("error"))

    @loader.unrestricted
    async def voicycmd(self, message: Message):
        """Recognize voice message"""
        reply = await message.get_reply_message()
        try:
            is_voice = (
                reply.video or reply.audio or reply.media.document.attributes[0].voice
            )
        except (AttributeError, IndexError):
            is_voice = False

        if not reply or not reply.media or not is_voice:
            await utils.answer(message, self.strings("voice_not_found"))
            return

        if message.out:
            await message.delete()

        await self.recognize(reply)

        if message.out:
            await message.delete()

    async def watcher(self, message: Message):
        try:
            if (
                utils.get_chat_id(message) not in self.get("chats", [])
                or not message.media
                or not message.video
                and not message.audio
                and not message.media.document.attributes[0].voice
            ):
                return
        except Exception:
            return
        
        if message.sender_id in self.config["ignore_users"]:
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
