# █ █ ▀ █▄▀ ▄▀█ █▀█ ▀    ▄▀█ ▀█▀ ▄▀█ █▀▄▀█ ▄▀█
# █▀█ █ █ █ █▀█ █▀▄ █ ▄  █▀█  █  █▀█ █ ▀ █ █▀█
#
#              © Copyright 2022
#
#          https://t.me/hikariatama
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://img.icons8.com/fluency/48/000000/code.png
# meta developer: @hikariatama
# scope: hikka_only

from .. import loader, utils

import requests
import logging
from telethon.tl.types import Message
import io

# requires: urllib requests

logger = logging.getLogger(__name__)


@loader.tds
class CarbonMod(loader.Module):
    """Create beautiful code images"""

    strings = {
        "name": "Carbon",
        "args": "🚫 <b>No args specified</b>",
        "loading": "🕐 <b>Loading...</b>",
    }

    async def client_ready(self, client, db):
        self._client = client

    async def carboncmd(self, message: Message):
        """<code> - Сделать красивую фотку кода"""
        args = utils.get_args_raw(message)

        try:
            code_from_message = (
                await self._client.download_file(message.media, bytes)
            ).decode("utf-8")
        except Exception:
            code_from_message = ""

        try:
            reply = await message.get_reply_message()
            code_from_reply = (await self._client.download_file(reply.media, bytes)).decode(
                "utf-8"
            )
        except Exception:
            code_from_reply = ""

        args = args or code_from_message or code_from_reply

        message = await utils.answer(message, self.strings("loading"))

        doc = io.BytesIO(
            (
                await utils.run_sync(
                    requests.post,
                    "https://carbonara-42.herokuapp.com/api/cook",
                    json={"code": args},
                )
            ).content
        )
        doc.name = "carbonized.jpg"

        await self._client.send_message(
            utils.get_chat_id(message),
            file=doc,
            force_document=(len(args.splitlines()) > 50),
        )
        await message.delete()
