#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://img.icons8.com/external-vitaliy-gorbachev-flat-vitaly-gorbachev/464/000000/external-sad-social-media-vitaliy-gorbachev-flat-vitaly-gorbachev.png
# meta banner: https://mods.hikariatama.ru/badges/emotionless.jpg
# meta developer: @hikarimods
# scope: hikka_only
# scope: hikka_min 1.6.3

import logging
import time
from typing import NamedTuple, Optional

from hikkatl.tl.functions.messages import ReadReactionsRequest
from hikkatl.tl.types import Message, UpdateMessageReactions

from .. import loader, utils

logger = logging.getLogger(__name__)


class Entry(NamedTuple):
    """Entry for reaction queue"""

    chat: int
    schedule: float
    top_msg_id: Optional[int] = None


@loader.tds
class EmotionlessMod(loader.Module):
    """Automatically reads reactions"""

    strings = {
        "name": "Emotionless",
        "state": (
            "<emoji document_id=5314591660192046611>😑</emoji> <b>Emotionless mode is"
            " now {}</b>"
        ),
        "on": "on",
        "off": "off",
    }

    strings_ru = {
        "state": (
            "<emoji document_id=5314591660192046611>😑</emoji> <b>Режим без реакций"
            " {}</b>"
        ),
        "on": "включен",
        "off": "выключен",
        "_cls_doc": "Автоматически читает реакции",
    }

    strings_de = {
        "state": (
            "<emoji document_id=5314591660192046611>😑</emoji> <b>Emotionless-Modus"
            " ist jetzt {}</b>"
        ),
        "on": "ein",
        "off": "aus",
        "_cls_doc": "Liest automatisch Reaktionen",
    }

    strings_uz = {
        "state": (
            "<emoji document_id=5314591660192046611>😑</emoji> <b>Emotionless rejimi"
            " {}</b>"
        ),
        "on": "yoqilgan",
        "off": "o'chirilgan",
        "_cls_doc": "Avtomatik ravishda reaksiyalarni o'qiydi",
    }

    strings_tr = {
        "state": (
            "<emoji document_id=5314591660192046611>😑</emoji> <b>Emotionless modu"
            " {}</b>"
        ),
        "on": "açık",
        "off": "kapalı",
        "_cls_doc": "Otomatik olarak tepkileri okur",
    }

    def __init__(self):
        self._queue = []
        self._flood_protect = []
        self._flood_protect_sample = 60
        self._threshold = 10

    @loader.command(
        ru_doc="Переключить авточтение реакций",
        de_doc="Schaltet das automatische Lesen von Reaktionen um",
        tr_doc="Otomatik tepki okumayı aç/kapa",
        uz_doc="Avtomatik reaksiya o'qishni yoqish/ochish",
    )
    async def noreacts(self, message: Message):
        """Toggle reactions auto-reader"""
        state = not self.get("state", False)
        self.set("state", state)
        await utils.answer(
            message,
            self.strings("state").format(self.strings("on" if state else "off")),
        )

    @loader.loop(interval=3, autostart=True)
    async def _queue_handler(self):
        if not self._queue:
            return

        chat, schedule, top_msg_id = self._queue[0]
        if schedule > time.time():
            return

        self._queue.pop(0)

        await self._client(ReadReactionsRequest(chat, top_msg_id))
        logger.debug(
            "Read reactions in queued peer %s, top_msg_id %s",
            chat,
            top_msg_id,
        )

    @loader.raw_handler(UpdateMessageReactions)
    async def _handler(self, update: UpdateMessageReactions):
        if (
            not self.get("state", False)
            or not hasattr(update, "reactions")
            or not hasattr(update.reactions, "recent_reactions")
            or not isinstance(update.reactions.recent_reactions, (list, set, tuple))
            or not any(i.unread for i in update.reactions.recent_reactions)
        ):
            return

        self._flood_protect = list(
            filter(lambda x: x > time.time(), self._flood_protect)
        )

        chat = next(
            getattr(update.peer, attribute)
            for attribute in {"channel_id", "chat_id", "user_id"}
            if hasattr(update.peer, attribute)
        )

        if len(self._flood_protect) > self._threshold:
            self._queue.append(
                Entry(
                    chat=chat,
                    schedule=self._flood_protect[0],
                    top_msg_id=update.top_msg_id,
                )
            )
            logger.debug("Flood protect triggered, chat %s added to queue", update)
            return

        self._flood_protect += [int(time.time()) + self._flood_protect_sample]

        await self._client(ReadReactionsRequest(update.peer, update.top_msg_id))
        logger.debug(
            "Read reaction in %s, top_msg_id %s", update.peer, update.top_msg_id
        )
