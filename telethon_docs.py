# █ █ ▀ █▄▀ ▄▀█ █▀█ ▀    ▄▀█ ▀█▀ ▄▀█ █▀▄▀█ ▄▀█
# █▀█ █ █ █ █▀█ █▀▄ █ ▄  █▀█  █  █▀█ █ ▀ █ █▀█
#
#              © Copyright 2022
#
#          https://t.me/hikariatama
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://img.icons8.com/fluency/48/000000/why-us-female.png
# meta developer: @hikariatama

from .. import loader, utils
from telethon.tl.types import Message
import logging

logger = logging.getLogger(__name__)


@loader.tds
class TelethonDocsMod(loader.Module):
    """Simple mod to quickly access telethon docs"""

    strings = {"name": "TelethonDocs"}

    async def client_ready(self, client, db):
        self._db = db
        self._client = client

    async def watcher(self, message: Message):
        if not getattr(message, "raw_text", None):
            return

        if not message.out or (
            not message.raw_text.startswith("#client")
            and not message.raw_text.startswith("#ref")
        ):
            return

        async with self._client.conversation("@nekoboy_telethon_bot") as conv:
            m = await conv.send_message(message.raw_text)
            r = await conv.get_response()

            await utils.answer(message, r.text)
            await m.delete()
            await r.delete()
