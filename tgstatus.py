#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒 Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://img.icons8.com/cotton/344/like--v2.png
# meta developer: @hikarimods
# meta banner: https://mods.hikariatama.ru/badges/tgstatus.jpg
# scope: hikka_only
# scope: hikka_min 1.4.2

import time
from .. import loader, utils
from telethon.tl.types import Message, MessageEntityCustomEmoji
from telethon.tl.functions.messages import (
    GetCustomEmojiDocumentsRequest,
    GetStickerSetRequest,
)
import logging

logger = logging.getLogger(__name__)


@loader.tds
class TgStatus(loader.Module):
    """Rotates Telegram status for Telegram Premium users only"""

    strings = {
        "name": "TgStatus",
        "noargs": (
            "<emoji document_id=6053166094816905153>💀</emoji> <b>You must specify"
            " interval of status rotation and at least one custom emoji!</b>"
        ),
        "status_started": (
            "<emoji document_id=5789838291234720526>💸</emoji> <b>Status rotation"
            " started!</b>\n\n<emoji document_id=5451732530048802485>⏳</emoji>"
            " <b>Interval: every {} minute(-s)</b>\n<b>Emojis: </b>{}"
        ),
        "status_stopped": (
            "<emoji document_id=5789838291234720526>💸</emoji> <b>Status rotation"
            " stopped!</b>"
        ),
        "no_status": (
            "<emoji document_id=5789838291234720526>💸</emoji> <b>Status rotation is not"
            " running!</b>"
        ),
    }

    strings_ru = {
        "noargs": (
            "<emoji document_id=6053166094816905153>💀</emoji> <b>Вы должны"
            " указать интервал смены статуса и хотя бы один кастомный эмодзи!</b>"
        ),
        "status_started": (
            "<emoji document_id=5789838291234720526>💸</emoji> <b>Смена статуса"
            " запущена!</b>\n\n<emoji document_id=5451732530048802485>⏳</emoji>"
            " <b>Интервал: каждые {} минут(-ы)</b>\n<b>Эмодзи: </b>{}"
        ),
        "status_stopped": (
            "<emoji document_id=5789838291234720526>💸</emoji> <b>Смена статуса"
            " остановлена!</b>"
        ),
        "no_status": (
            "<emoji document_id=5789838291234720526>💸</emoji> <b>Смена статуса не"
            " запущена!</b>"
        ),
    }

    async def client_ready(self):
        if not self._client.hikka_me.premium:
            raise loader.LoadError("⭐️ This module is for Telegram Premium only!")

        self.status = self.pointer("status", [])
        self.status_loop.start()

    @loader.loop(interval=1)
    async def status_loop(self):
        if (
            not self.status
            or not self.get("interval")
            or self.get("last_change", 0) + self.get("interval") > time.time()
        ):
            return

        await self._client.set_status(self.status[self.get("current_status", 0)])
        logger.debug(f"Status changed to {self.status[self.get('current_status', 0)]}")
        self.set("current_status", self.get("current_status", 0) + 1)

        if self.get("current_status") >= len(self.status):
            self.set("current_status", 0)

        self.set("last_change", int(time.time()))

    @loader.command(
        ru_doc=(
            "<кастомные эмодзи для статуса> <интервал в минутах> - Запустить ротацию"
            " статуса с интервалом в минутах"
        )
    )
    async def tgstatus(self, message: Message):
        """<custom emojis for statuses> <time to rotate in minutes> - Start status rotation with interval in minutes
        """
        args = utils.get_args_raw(message)
        args = "".join(s for s in args if s.isdigit())
        if not args or not any(
            isinstance(entity, MessageEntityCustomEmoji) for entity in message.entities
        ):
            await utils.answer(message, self.strings("noargs"))
            return

        self.status.clear()
        self.status.extend(
            [
                entity.document_id
                for entity in message.entities
                if isinstance(entity, MessageEntityCustomEmoji)
            ]
        )
        self.set("interval", int(args) * 60)
        self.set("last_change", 0)
        self.set("current_status", 0)
        await utils.answer(
            message,
            self.strings("status_started").format(
                args,
                "".join(
                    f"<emoji document_id={emoji.document_id}>▫️</emoji>"
                    for emoji in message.entities
                    if isinstance(emoji, MessageEntityCustomEmoji)
                ),
            ),
        )

    @loader.command(
        ru_doc=(
            "<кастомные эмодзи для получения паков> <интервал в минутах> - Запустить"
            " ротацию статуса с интервалом в минутах, используя полный пак указанных"
            " эмодзи"
        )
    )
    async def tgstatuspack(self, message: Message):
        """<custom emojis for pack search> <time to rotate in minutes> - Start status rotation with interval in minutes using full pack of specified emojis
        """
        args = utils.get_args_raw(message)
        args = "".join(s for s in args if s.isdigit())
        if not args or not any(
            isinstance(entity, MessageEntityCustomEmoji) for entity in message.entities
        ):
            await utils.answer(message, self.strings("noargs"))
            return

        self.status.clear()
        self.status.extend(
            utils.array_sum(
                [
                    [
                        emoji.id
                        for emoji in (
                            await self._client(GetStickerSetRequest(stickerset, hash=0))
                        ).documents
                    ]
                    for stickerset in filter(
                        lambda x: x,
                        [
                            next(
                                (
                                    attr.stickerset
                                    for attr in emoji.attributes
                                    if hasattr(attr, "stickerset")
                                ),
                                None,
                            )
                            for emoji in await self._client(
                                GetCustomEmojiDocumentsRequest(
                                    [
                                        entity.document_id
                                        for entity in message.entities
                                        if isinstance(entity, MessageEntityCustomEmoji)
                                    ]
                                )
                            )
                        ],
                    )
                ]
            )
        )
        self.set("interval", int(args) * 60)
        self.set("last_change", 0)
        self.set("current_status", 0)
        await utils.answer(
            message,
            self.strings("status_started").format(
                args,
                "".join(
                    f"<emoji document_id={emoji}>▫️</emoji>" for emoji in self.status
                ),
            ),
        )

    @loader.command(ru_doc="Остановить статус")
    async def untgstatus(self, message: Message):
        """Stop status rotation"""
        if not self.status:
            await utils.answer(message, self.strings("no_status"))
            return

        self.status.clear()
        self.set("interval", 0)
        self.set("last_change", 0)
        self.set("current_status", 0)

        await utils.answer(message, self.strings("status_stopped"))
