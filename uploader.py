# █ █ ▀ █▄▀ ▄▀█ █▀█ ▀    ▄▀█ ▀█▀ ▄▀█ █▀▄▀█ ▄▀█
# █▀█ █ █ █ █▀█ █▀▄ █ ▄  █▀█  █  █▀█ █ ▀ █ █▀█
#
#              © Copyright 2022
#
#          https://t.me/hikariatama
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://img.icons8.com/fluency/48/000000/upload-to-cloud.png
# meta developer: @hikariatama

import logging
import io
import requests
from telethon.errors.rpcerrorlist import YouBlockedUserError
import imghdr
import random
import re
from telethon.tl.types import Message

from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class FileUploaderMod(loader.Module):
    """Different engines file uploader"""

    strings = {
        "name": "Uploader",
        "uploading": "📤 <b>Uploading...</b>",
        "noargs": "🚫 <b>No file specified</b>",
        "err": "🚫 <b>Upload error</b>",
        "uploaded": "🌐 <code>{}</code>",
        "imgur_blocked": "🚫 <b>Unban @imgurbot_bot</b>",
        "not_an_image": "🚫 <b>This platform only supports images</b>",
    }

    async def client_ready(self, client, db):
        self._client = client
        self._db = db

    async def get_media(self, message: Message):
        reply = await message.get_reply_message()
        m = None
        if reply and reply.media:
            m = reply
        elif message.media:
            m = message
        elif not reply:
            await utils.answer(message, self.strings("noargs"))
            return False

        if not m:
            file = io.BytesIO(bytes(reply.raw_text, "utf-8"))
            file.name = "file.txt"
        else:
            file = io.BytesIO(await self._client.download_file(m.media, bytes))
            file.name = (
                m.file.name
                or (
                    "".join(
                        [
                            random.choice("abcdefghijklmnopqrstuvwxyz1234567890")
                            for _ in range(16)
                        ]
                    )
                )
                + m.file.ext
            )

        return file

    async def get_image(self, message: Message):
        file = await self.get_media(message)
        if not file:
            return False
        if imghdr.what(file) not in ["gif", "png", "jpg", "jpeg", "tiff", "bmp"]:
            await utils.answer(message, self.strings("not_an_image"))
            return False
        return file

    async def x0cmd(self, message: Message):
        """Upload to x0.at"""
        await utils.answer(message, self.strings("uploading"))
        file = await self.get_media(message)
        if not file:
            return

        try:
            x0at = requests.post("https://x0.at", files={"file": file})
        except ConnectionError:
            await utils.answer(message, self.strings("err"))
            return

        url = x0at.text
        await utils.answer(message, self.strings("uploaded").format(url))

    async def imgurcmd(self, message: Message):
        """Upload to imgur.com"""
        await utils.answer(message, self.strings("uploading"))
        file = await self.get_image(message)
        if not file:
            return
        chat = "@ImgUploadBot"

        async with self._client.conversation(chat) as conv:
            try:
                m = await conv.send_message(file=file)
                response = await conv.get_response()
            except YouBlockedUserError:
                await utils.answer(message, self.strings("imgur_blocked"))
                return

            await m.delete()
            await response.delete()

            try:
                url = (
                    re.search(
                        r'<meta property="og:image" data-react-helmet="true" content="(.*?)"',
                        requests.get(response.raw_text).text,
                    )
                    .group(1)
                    .split("?")[0]
                )
            except Exception:
                url = response.raw_text

            await utils.answer(message, self.strings("uploaded").format(url))

    async def oxocmd(self, message: Message):
        """Upload to 0x0.st"""
        await utils.answer(message, self.strings("uploading"))
        file = await self.get_media(message)
        if not file:
            return

        try:
            x0at = requests.post("https://0x0.st", files={"file": file})
        except ConnectionError:
            await utils.answer(message, self.strings("err"))
            return

        url = x0at.text
        await utils.answer(message, self.strings("uploaded").format(url))
