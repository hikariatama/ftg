# █ █ ▀ █▄▀ ▄▀█ █▀█ ▀    ▄▀█ ▀█▀ ▄▀█ █▀▄▀█ ▄▀█
# █▀█ █ █ █ █▀█ █▀▄ █ ▄  █▀█  █  █▀█ █ ▀ █ █▀█
#
#              © Copyright 2022
#
#          https://t.me/hikariatama
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://img.icons8.com/external-vitaliy-gorbachev-flat-vitaly-gorbachev/464/000000/external-sad-social-media-vitaliy-gorbachev-flat-vitaly-gorbachev.png
# meta developer: @hikariatama
# scope: hikka_only

from .. import loader, utils
from telethon.tl.types import Message
from telethon.events import Raw
from telethon.tl.types import UpdateMessageReactions
from telethon.tl.functions.messages import ReadReactionsRequest
from telethon.utils import get_input_peer
import logging
import asyncio
import time

logger = logging.getLogger(__name__)


@loader.tds
class EmotionlessMod(loader.Module):
    """Automatically reads reactions"""

    strings = {"name": "Emotionless", "state": "😑 <b>Emotionless mode is now {}</b>"}

    async def client_ready(self, client, db):
        self._db = db
        self._client = client
        self._flood_protect = []
        self._queue = {}
        self._flood_protect_sample = 60
        self._threshold = 10

        self.handler = (self._handler, Raw)
        client.add_event_handler(*self.handler)
        self._task = asyncio.ensure_future(self._queue_handler())

    async def on_unload(self):
        self._client.remove_event_handler(*self.handler)
        self._task.cancel()

    async def noreactscmd(self, message: Message):
        """Toggle reactions auto-reader"""
        state = not self.get("state", False)
        self.set("state", state)
        await utils.answer(
            message, self.strings("state").format("on" if state else "off")
        )

    async def _queue_handler(self):
        while True:

            for chat, schedule in self._queue.copy().items():
                if schedule < time.time():
                    await self._client(ReadReactionsRequest(get_input_peer(chat)))
                    logger.debug(f"Read reactions in queued peer {chat}")
                    del self._queue[chat]

            await asyncio.sleep(5)

    async def _handler(self, event: Raw):
        try:
            if not isinstance(event, UpdateMessageReactions):
                return

            if not self.get("state", False):
                return

            if (
                not hasattr(event, "reactions")
                or not hasattr(event.reactions, "recent_reactions")
                or not isinstance(event.reactions.recent_reactions, (list, set, tuple))
                or not any(i.unread for i in event.reactions.recent_reactions)
            ):
                return

            self._flood_protect = list(filter(lambda x: x > time.time(), self._flood_protect))

            if len(self._flood_protect) > self._threshold:
                self._queue[utils.get_chat_id(event)] = time.time() + 15
                logger.debug(f"Flood protect triggered, chat {event} added to queue")
                return

            self._flood_protect += [round(time.time()) + self._flood_protect_sample]

            await self._client(ReadReactionsRequest(event.peer))
            logger.debug(f"Read reaction in {event.peer}")
        except Exception:
            logger.exception("Caught exception in Emotionless")
