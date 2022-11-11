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
# scope: hikka_min 1.5.2

import logging
import time

from telethon.tl.functions.messages import ReadReactionsRequest
from telethon.tl.types import Message, UpdateMessageReactions
from telethon.utils import get_input_peer

from .. import loader, utils

logger = logging.getLogger(__name__)


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

    strings_hi = {
        "state": (
            "<emoji document_id=5314591660192046611>😑</emoji> <b>एमोशनलेस मोड {}</b>"
        ),
        "on": "चालू",
        "off": "बंद",
        "_cls_doc": "ऑटोमैटिकली रिएक्शन पढ़ता है",
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
        self._queue = {}
        self._flood_protect = []
        self._flood_protect_sample = 60
        self._threshold = 10

    @loader.command(
        ru_doc="Переключить авточтение реакций",
        de_doc="Schaltet das automatische Lesen von Reaktionen um",
        tr_doc="Otomatik tepki okumayı aç/kapa",
        hi_doc="ऑटोमैटिक रिएक्शन पढ़ना चालू/बंद करें",
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

    @loader.loop(interval=5, autostart=True)
    async def _queue_handler(self):
        for chat, schedule in self._queue.copy().items():
            if schedule < time.time():
                await self._client(ReadReactionsRequest(get_input_peer(chat)))
                logger.debug("Read reactions in queued peer %s", chat)
                self._queue.pop(chat)

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
            self._queue[chat] = time.time() + 15
            logger.debug("Flood protect triggered, chat %s added to queue", update)
            return

        self._flood_protect += [int(time.time()) + self._flood_protect_sample]

        await self._client(ReadReactionsRequest(update.peer))
        logger.debug("Read reaction in %s", update.peer)
