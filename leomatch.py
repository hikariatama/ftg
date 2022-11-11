#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒 Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta desc: Simplifies the interaction with @leomatchbot - Rejects slag, allows you to create filters by age, cities, blacklisted words.
# meta pic: https://static.hikari.gay/leomatch_icon.png
# meta banner: https://mods.hikariatama.ru/badges/leomatch.jpg
# meta developer: @hikarimods
# requires: russian-names
# scope: hikka_only
# scope: hikka_min 1.3.0

__version__ = (2, 0, 2)

import asyncio
import logging
import re
import time
from typing import Iterable, Optional

from russian_names import RussianNames
from telethon.tl.types import Message

from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class LeomatchMod(loader.Module):
    """Simplifies the interaction with @leomatchbot - Rejects slag, allows you to create filters by age, cities, blacklisted words. Check .config for more info
    """

    strings = {"name": "Leomatch"}

    strings_ru = {
        "_cls_doc": (
            "Упрощает взаимодействие с @leomatchbot - отклоняет шлак, позволяет"
            " создавать фильтры по возрасту, городам, черному списку слов. Загляни в"
            " .config для подробной информации"
        ),
    }

    _last_decline = 0
    _queue = []
    _groups = {}

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "min_age",
                0,
                "Минимальный возраст собеседника - будет автоматически отклонять всех,"
                " кто младше",
                validator=loader.validators.Integer(minimum=0),
            ),
            loader.ConfigValue(
                "max_age",
                100,
                "Максимальный возраст собеседника - будет автоматически отклонять всех,"
                " кто старше",
                validator=loader.validators.Integer(minimum=0),
            ),
            loader.ConfigValue(
                "blacklist_cities",
                [],
                "Список городов, пользователи из которых будут автоматически"
                " отклоняться",
                validator=loader.validators.Series(),
            ),
            loader.ConfigValue(
                "whitelist_cities",
                [],
                "Список городов для белого списка. Пользователи из других городов будут"
                " автоматически отклоняться",
                validator=loader.validators.Series(),
            ),
            loader.ConfigValue(
                "blacklist_words",
                [],
                "Если в анкете пользователя есть слово из этого списка, она будет"
                " автоматически отклонена",
                validator=loader.validators.Series(),
            ),
            loader.ConfigValue(
                "whitelist_words",
                [],
                "Если в анкете пользователя есть нет слов из этого списка, она будет"
                " автоматически отклонена",
                validator=loader.validators.Series(),
            ),
            loader.ConfigValue(
                "decline_slag",
                True,
                "Отклонять ли шлак (Подпишитесь на наш ТикТок и др.)",
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "enable",
                True,
                "Включить ли модуль",
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "minimal_len",
                0,
                "Минимальное количество слов в анкете",
                validator=loader.validators.Integer(minimum=0),
            ),
            loader.ConfigValue(
                "log",
                True,
                "Отправлять в логи информацию о причинах отклонения анкет",
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "delay",
                5,
                "Задержка между автоматическим отклонением анкет",
                validator=loader.validators.Integer(minimum=3),
            ),
            loader.ConfigValue(
                "no_female",
                False,
                "Автоматически отклонять девушек",
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "no_male",
                False,
                "Автоматически отклонять парней",
                validator=loader.validators.Boolean(),
            ),
        )

    async def client_ready(self):
        names = RussianNames()
        await utils.run_sync(names._fill_base)

        self.female_names = map(lambda x: x.lower(), names._base["woman"]["name"])
        self.male_names = map(lambda x: x.lower(), names._base["man"]["name"])

    @loader.loop(interval=1, autostart=True)
    async def loop(self):
        if not self._queue:
            return

        if self._last_decline + self.config["delay"] > time.time():
            await asyncio.sleep(self._last_decline + self.config["delay"] - time.time())

        self._last_decline = time.time()

        log, answer = self._queue.pop(0)

        async with self._client.conversation(1234060895) as conv:
            m = await conv.send_message(answer)
            await conv.get_response()

        await m.delete()

        if self.config["log"] and log:
            logger.info(log)

    async def _decline(
        self,
        message: Message,
        log: Optional[str] = None,
        answer: Optional[str] = "👎",
    ):
        for m in [message] + (
            [m for m in self._groups[message.grouped_id]]
            if message.grouped_id and message.grouped_id in self._groups
            else []
        ):
            await m.delete()

        self._queue += [(log, answer)]

    @staticmethod
    def _in(needle: str, haystack: Iterable, alter: str) -> bool:
        """
        Checks for occurence of needle in haystack using smart method
        :param needle: string to search for
        :param haystack: iterable to search in
        :param alter: string to search in if needle is not a one word
        :return: True if needle is found in haystack, False otherwise
        """
        return (
            True
            if needle.strip().lower() in map(lambda x: x.lower().strip(), haystack)
            else " " in needle and needle.strip().lower() in alter.lower()
        )

    @loader.watcher("only_messages", "only_pm", "in")
    async def watcher(self, message: Message):
        if (
            self._queue
            and utils.get_chat_id(message) == 1234060895
            and message.out
            and self.config["enable"]
        ):
            self._queue = []
            logger.info("Останавливаюсь, т.к. ты отправил сообщение")
            return

        if message.sender_id != 1234060895 or not self.config["enable"]:
            return

        if (
            "Пригласи друзей и получи больше" in message.raw_text
            and "Твоя статистика" not in message.raw_text
        ):
            self._queue = []
            logger.info("Останавливаюсь, т.к. закончились доступные лайки")
            return

        if message.grouped_id:
            self._groups.setdefault(message.grouped_id, []).append(message)

        if self.config["decline_slag"] and (
            (
                "Подпишись на канал Дайвинчика" in message.raw_text
                and "https://t.me/leoday" in message.text
            )
            or (
                "Бот не запрашивает личные данные и не идентифицирует пользователей по"
                " паспортным данным"
                in message.raw_text
            )
            or (
                "хочешь больше просмотров в TikTok?" in message.raw_text
                and "tiktok.com/tag/дайвинчик" in message.raw_text
            )
            or (
                "Пришли свое расположение и увидишь анкеты рядом с тобой"
                in message.raw_text
            )
        ):
            await self._decline(
                message,
                "Отклонил какой-то шлак",
                "Продолжить просмотр анкет",
            )
            return

        if self.config["decline_slag"] and message.raw_text == "Это все, идем дальше?":
            await self._decline(
                message,
                "Автоматически продолжаю просмотр анкет",
                "Смотреть анкеты",
            )
            return

        if (
            message.raw_text.count(",") < 2
            or message.raw_text.startswith("Кому-то понравилась твоя анкета:")
            or "Отлично! Надеюсь хорошо проведете время ;) Начинай общаться"
            in message.raw_text
        ):
            return

        words = re.sub(
            r" {2,}",
            " ",
            "".join(
                symbol
                if symbol
                in "abcdefghijklmnopqrstuvwxyzёйцукенгшщзхъфывапролджэячсмитьбю1234567890 "
                else " "
                for symbol in (
                    ""
                    if len(message.raw_text.lower().split(",", maxsplit=2)) < 3
                    or "–" not in message.raw_text
                    else message.raw_text.lower()
                    .split(",", maxsplit=2)[2]
                    .split("–")[1]
                )
            ),
        ).split()

        user = (
            message.raw_text.split("–")[0].strip()
            if "–" in message.raw_text
            else message.raw_text
        )

        user_name = user.split(",")[0].strip().lower()
        if (
            self.config["no_female"]
            and user_name in self.female_names
            or self.config["no_male"]
            and user_name in self.male_names
        ):
            await self._decline(message, f"{user} отклонен по несовпадению пола")

        if self.config["minimal_len"] and len(list(words)) < self.config["minimal_len"]:
            await self._decline(
                message,
                f"{user} отклонен из-за слишком короткой анкеты",
            )
            return

        if (
            self.config["blacklist_cities"]
            and len(message.raw_text.split(",")) >= 3
            and message.raw_text.split(",")[2].split()[0].lower().strip()
            in map(lambda x: x.lower().strip(), self.config["blacklist_cities"])
        ):
            await self._decline(
                message,
                f"{user} отклонен из-за наличия города в черном списке",
            )
            return

        if (
            self.config["whitelist_cities"]
            and len(message.raw_text.split(",")) >= 3
            and message.raw_text.split(",")[2].split()[0].lower().strip()
            not in map(lambda x: x.lower().strip(), self.config["whitelist_cities"])
        ):
            await self._decline(
                message,
                f"{user} отклонен из-за отсутствия города в белом списке",
            )
            return

        if self.config["blacklist_words"] and any(
            self._in(word, words, message.raw_text)
            for word in self.config["blacklist_words"]
        ):
            await self._decline(message, f"{user} отклонен из-за слов в черном списке")
            return

        if self.config["whitelist_words"] and not any(
            self._in(word, words, message.raw_text)
            for word in self.config["whitelist_words"]
        ):
            await self._decline(
                message,
                f"{user} отклонен из-за отсутствия в анкете слов из белого списка",
            )
            return

        if (
            self.config["min_age"]
            and len(message.raw_text.split(",")) >= 2
            and message.raw_text.split(",")[1].strip().isdigit()
            and int(message.raw_text.split(",")[1].strip()) < self.config["min_age"]
        ):
            await self._decline(message, f"{user} отклонен из-за младшего возраста")
            return

        if (
            self.config["max_age"]
            and len(message.raw_text.split(",")) >= 2
            and message.raw_text.split(",")[1].strip().isdigit()
            and int(message.raw_text.split(",")[1].strip()) > self.config["max_age"]
        ):
            await self._decline(message, f"{user} отклонен из-за старшего возраста")
            return
