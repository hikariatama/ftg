#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒 Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://static.hikari.gay/v2a_icon.png
# meta developer: @hikarimods
# meta banner: https://mods.hikariatama.ru/badges/v2a.jpg
# scope: ffmpeg
# scope: hikka_only
# scope: hikka_min 1.3.0

import asyncio
import io
import os
import logging
import tempfile

from telethon.tl.types import Message, DocumentAttributeAudio
import telethon.utils as tlutils

from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class Video2Audio(loader.Module):
    """Converts video \ round messages to audio \ voice messages"""

    strings = {
        "name": "Video2Audio",
        "no_video": "🚫 <b>Reply to video required</b>",
        "converting": "🧚‍♀️ <b>Converting...</b>",
        "error": "🚫 <b>Error while converting</b>",
    }
    strings_ru = {
        "no_video": "🚫 <b>Ответь на видео</b>",
        "converting": "🧚‍♀️ <b>Конвертирую...</b>",
        "_cls_doc": "Конвертирует видео в аудио",
        "error": "🚫 <b>Ошибка при конвертировании</b>",
    }

    async def client_ready(self):
        self.v2a = await self.import_lib(
            "https://libs.hikariatama.ru/v2a.py",
            suspend_on_error=True,
        )

    @loader.command(
        ru_doc=(
            "<ответ на видео> [-vm] [-b] - конвертировать видео в аудио\n-vm -"
            " Отправить голосовое сообщение"
        )
    )
    async def v2acmd(self, message: Message):
        """<reply> [-vm] [-b] - Convert video to audio
        -vm - Use voice message instead"""
        use_voicemessage = "-vm" in utils.get_args_raw(message)
        reply = await message.get_reply_message()
        if not reply or not reply.video:
            await utils.answer(message, self.strings("no_video"))
            return

        message = await utils.answer(message, self.strings("converting"))
        video = await self._client.download_media(reply, bytes)

        out = f"audio.{'ogg' if use_voicemessage else 'mp3'}"
        try:
            audio = await self.v2a.convert(video, out)
        except Exception:
            await utils.answer(message, self.strings("error"))
            return

        audiofile = io.BytesIO(audio)
        audiofile.name = out

        await self._client.send_file(
            message.peer_id,
            audiofile,
            voice_note=use_voicemessage,
            reply_to=reply.id,
            attributes=[
                DocumentAttributeAudio(
                    duration=2147483647,
                    voice=use_voicemessage,
                    **(
                        {
                            "waveform": tlutils.encode_waveform(
                                bytes(
                                    (
                                        *tuple(range(0, 30, 5)),
                                        *reversed(tuple(range(0, 30, 5))),
                                    )
                                )
                                * 20
                            )
                        }
                        if use_voicemessage
                        else {}
                    ),
                )
            ],
        )

        if message.out:
            await message.delete()
