__version__ = (2, 0, 0)

#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://static.hikari.gay/bfg_icon.png
# meta banner: https://mods.hikariatama.ru/badges/bfg.jpg
# meta developer: @hikarimods
# scope: hikka_only
# scop: hikka_min 1.3.0

import asyncio
from .. import loader, utils

import time
import logging

from telethon.events import NewMessage
from telethon.tl.types import Message
from telethon.tl.functions.messages import ReadMentionsRequest
from telethon.tl.functions.contacts import UnblockRequest
from telethon.errors.rpcerrorlist import YouBlockedUserError

logger = logging.getLogger(__name__)


class Mining:
    async def _automining(self) -> bool:
        async with self._client.conversation(self._bot) as conv:
            await conv.send_message("Моя шахта")
            r = await conv.get_response()
            mining_exp = int(
                "".join(
                    s
                    for s in r.raw_text.splitlines()[1].split()[2].strip()
                    if s.isdigit()
                )
            )
            self.set("mining_exp", mining_exp)
            energy = int(
                "".join(
                    s
                    for s in r.raw_text.splitlines()[2].split()[2].strip()
                    if s.isdigit()
                )
            )

        if energy == 0:
            return False

        resource = next(
            resource
            for range_, resource in self._resources_map.items()
            if mining_exp in range_
        )

        async with self._client.conversation(self._bot) as conv:
            while energy > 0:
                await conv.send_message(f"копать {resource}")
                r = await conv.get_response()
                if "у вас закончилась" in r.raw_text:
                    break

                if "Энергия" in r.raw_text:
                    energy = int(r.raw_text.split("Энергия:")[1].split(",")[0].strip())

                await asyncio.sleep(0.5)

        return True

    async def _sell_btc(self) -> bool:
        async with self._client.conversation(self._bot) as conv:
            await conv.send_message("Продать биткоины")
            await conv.get_response()

        return True

    async def _mining_sell(self) -> bool:
        if not self.get("mining_exp"):
            return False

        resources = []
        for range_, resource in self._resources_map.items():
            resources += [resource]
            if self.get("mining_exp") in range_:
                break

        async with self._client.conversation(self._bot) as conv:
            for resource in self._resources_map.values():
                if resource == "материю":
                    continue

                await conv.send_message(f"продать {resource}")
                await conv.get_response()


class Bonuses:
    async def _daily(self):
        async with self._client.conversation(self._bot) as conv:
            await conv.send_message("Ежедневный бонус")
            r = await conv.get_response()
            if "ты уже получал" not in r.raw_text:
                await asyncio.sleep(2)
                await conv.send_message("Ежедневный бонус")
                r = await conv.get_response()

            hours, minutes = (
                r.raw_text.split("ты сможешь получить через")[1].strip().split()
            )
            hours, minutes = int(hours[:-1]), int(minutes[:-1])
            time_ = hours * 60 * 60 + minutes * 60
            self.set("daily", int(time.time() + time_ + 60))
            return True

    async def _treasures(self):
        async with self._client.conversation(self._bot) as conv:
            await conv.send_message("Ограбить казну")
            await conv.get_response()
            self.set("treasures", int(time.time() + 24 * 60 * 60))


class Potions:
    async def _create_poisons(self) -> bool:
        async with self._client.conversation(self._bot) as conv:
            await conv.send_message("Инвентарь")
            r = await conv.get_response()
            if "Зёрна:" not in r.raw_text:
                self.set("poisons", int(time.time() + 30 * 60))
                return False

            grains = int(
                "".join(
                    s
                    for s in r.raw_text.split("Зёрна:")[1].strip().split(" ")[0]
                    if s.isdigit()
                )
            )

            any_ = False

            for _ in range(grains // 40):
                await conv.send_message("Создать зелье 1")
                await conv.get_response()
                await asyncio.sleep(0.5)
                any_ = True

        if any_:
            self.set("automining", 0)

        self.set("poisons", int(time.time() + 30 * 60))
        return True


@loader.tds
class BFG2Mod(loader.Module, Mining, Bonuses, Potions):
    """Tasks automation for @bforgame_bot"""

    strings = {"name": "BFG"}

    strings_ru = {"_cls_doc": "Фарм в @bforgame_bot"}

    _request_timeout = 3
    _last_iter = 0
    _cache = {}
    _resources_map = {
        range(0, 500): "железо",
        range(500, 2000): "золото",
        range(2000, 10000): "алмазы",
        range(10000, 25000): "аметисты",
        range(25000, 60000): "аквамарин",
        range(60000, 100000): "изумруды",
        range(100000, 500000): "материю",
        range(
            500000, 10**50
        ): "плазму",  # We don't care about the size of value, bc it's range
    }
    _bot = "@bforgame_bot"

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "autodaily",
                True,
                "Автоматически собирать ежедневный бонус",
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "autotreasures",
                True,
                "Автоматически грабить мэрию",
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "automining",
                True,
                "Автоматически копать шахту и продавать все ресурсы, кроме материи",
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "autofarm",
                True,
                "Автоматически собирать налоги и прибыль с фермы",
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "autogarden",
                True,
                "Автоматически собирать налоги, собирать прибыль и поливать сад",
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "autogenerator",
                True,
                "Автоматически собирать налоги и прибыль с бизнеса",
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "autobusiness",
                True,
                "Автоматически собирать налоги и прибыль с бизнеса",
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "autopotions",
                True,
                "Автоматически варить зелья",
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "sell_btc",
                False,
                "Автоматически продавать биткоины",
                validator=loader.validators.Boolean(),
            ),
        )

    async def client_ready(self):
        try:
            await self._client.send_message(
                self._bot,
                "💫 <i>~модуль автоматизации bfg от hikari. запущен~~</i>",
            )
        except YouBlockedUserError:
            await self._client(UnblockRequest(self._bot))
            await self._client.send_message(
                self._bot,
                "💫 <i>~модуль автоматизации bfg от hikari. запущен~~</i>",
            )

    async def _garden(self) -> bool:
        try:
            message = await self._get_msg("Мой сад")
            if not message:
                return False

            await message.click(data=b"payTaxesGarden")
            await asyncio.sleep(1)
            await message.click(data=b"pourGarden")
            await asyncio.sleep(1)
            await message.click(data=b"collectIncomeGarden")
            return True
        except Exception:
            logger.exception("Can't process BFG click")
            self.set("garden", None)
            return False

    async def _generator(self) -> bool:
        try:
            message = await self._get_msg("Мой генератор")
            if not message:
                return False

            await message.click(data=b"payTaxesGenerator")
            await asyncio.sleep(1)
            await message.click(data=b"collectIncomeGenerator")
            return True
        except Exception:
            logger.exception("Can't process BFG click")
            self.set("generator", None)
            return False

    async def _business(self) -> bool:
        try:
            message = await self._get_msg("Мой бизнес")
            if not message:
                return False

            await message.click(data=b"payTaxes")
            await asyncio.sleep(1)
            await message.click(data=b"collectIncome")
            return True
        except Exception:
            logger.exception("Can't process BFG click")
            self.set("business", None)
            return False

    async def _farm(self) -> bool:
        try:
            message = await self._get_msg("Моя ферма")
            if not message:
                return False

            await message.click(data=b"payTaxesFarm")
            await asyncio.sleep(1)
            await message.click(data=b"collectIncomeFarm")
            return True
        except Exception:
            logger.exception("Can't process BFG click")
            self.set("farm", None)
            return False

    async def _get_msg(self, key: str) -> Message:
        async with self._client.conversation(self._bot) as conv:
            await conv.send_message(key)
            r = await conv.get_response()
            if "чтобы построить введите команду" in r.raw_text:
                key = {
                    "Мой генератор": "generator",
                    "Моя ферма": "farm",
                    "Мой сад": "garden",
                    "Мой бизнес": "business",
                }[key]
                self.config[f"auto{key}"] = False
                return False

            return r

    @loader.loop(interval=15, autostart=True)
    async def loop(self):
        any_ = False
        if not self.get("fee_time") or self.get("fee_time") < time.time():
            if self.config["autopotions"]:
                await self._create_poisons()
                any_ = True
                await asyncio.sleep(5)

            if self.config["autofarm"]:
                await self._farm()
                any_ = True
                await asyncio.sleep(5)

            if self.config["autogarden"]:
                await self._garden()
                any_ = True
                await asyncio.sleep(5)

            if self.config["autogenerator"]:
                await self._generator()
                any_ = True
                await asyncio.sleep(5)

            if self.config["autobusiness"]:
                await self._business()
                any_ = True
                await asyncio.sleep(5)

            if self.config["automining"]:
                await self._automining()
                await self._mining_sell()
                any_ = True
                await asyncio.sleep(5)

            if self.config["sell_btc"]:
                await self._sell_btc()
                any_ = True
                await asyncio.sleep(5)

            if any_:
                self.set("fee_time", int(time.time() + 60 * 60))

        if self.config["autodaily"] and (
            not self.get("daily") or self.get("daily") < time.time()
        ):
            await self._daily()
            any_ = True
            await asyncio.sleep(5)

        if self.config["autotreasures"] and (
            not self.get("treasures") or self.get("treasures") < time.time()
        ):
            await self._treasures()
            any_ = True

        if any_:
            await self._client(ReadMentionsRequest(self._bot))

    @loader.command(ru_doc="[уровни] - покупка уровней для фермы")
    async def farmlvlcmd(self, message: Message):
        """[levels] - Level-up farm for specfied amount of levels"""
        args = utils.get_args_raw(message)
        if args and not args.isdigit():
            await utils.answer(message, "🚫 <b>Некорректное количество уровней</b>")
            return

        message = await utils.answer(message, "🫶 <b>Улучшаю ферму</b>")

        levels = 0 if not args else int(args)
        chunk = 0
        enchanced = 0

        while levels:
            async with self._client.conversation(self._bot) as conv:
                await conv.send_message("Моя ферма")
                r = await conv.get_response()
                if "Видеокарты: 100" in r.raw_text:
                    await utils.answer(message, "🫶 <b>Ферма улучшена до максимума</b>")
                    return

                while chunk < 10 and levels:
                    await r.click(data=b"buyFarmCard")
                    await conv.wait_event(
                        NewMessage(outgoing=False, chats=conv.chat_id)
                    )
                    resp = (await self._client.get_messages(self._bot, limit=1))[0]
                    if "вы успешно увеличили" not in resp.raw_text:
                        await utils.answer(
                            message,
                            f"🫶 <b>Ферма улучшена на {enchanced} уровней. Закончились"
                            " деньги</b>",
                        )
                        return

                    enchanced += 1
                    levels -= 1
                    chunk += 1

        await utils.answer(message, f"🫶 <b>Ферма улучшена на {enchanced} уровней.</b>")

    @loader.command(
        ru_doc="[уровни] - покупка уровней для бизнеса (территория + сам бизнес)"
    )
    async def businesslvlcmd(self, message: Message):
        """[levels] - Level-up business for specfied amount of levels (territory + business itself)
        """
        args = utils.get_args_raw(message)
        if args and not args.isdigit():
            await utils.answer(message, "🚫 <b>Некорректное количество уровней</b>")
            return

        message = await utils.answer(message, "🫶 <b>Улучшаю бизнес</b>")

        levels = 0 if not args else int(args)
        chunk = 0
        enchanced = 0

        while levels:
            async with self._client.conversation(self._bot) as conv:
                await conv.send_message("Мой бизнес")
                r = await conv.get_response()
                while chunk < 10 and levels:
                    await r.click(data=b"upTerritory")
                    await conv.wait_event(
                        NewMessage(outgoing=False, chats=conv.chat_id)
                    )
                    resp = (await self._client.get_messages(self._bot, limit=1))[0]
                    if "вы достигли максимального размера" in resp.raw_text:
                        await utils.answer(
                            message,
                            f"🫶 <b>Бизнес улучшен на {enchanced} уровней. Закончились"
                            " деньги</b>",
                        )
                        return

                    await r.click(data=b"upBusiness")
                    await conv.wait_event(
                        NewMessage(outgoing=False, chats=conv.chat_id)
                    )
                    resp = (await self._client.get_messages(self._bot, limit=1))[0]
                    if "чтобы увеличить бизнес" in resp.raw_text:
                        await utils.answer(
                            message,
                            f"🫶 <b>Бизнес улучшен на {enchanced} уровней. Закончились"
                            " деньги</b>",
                        )
                        return

                    enchanced += 1
                    levels -= 1
                    chunk += 1

        await utils.answer(message, f"🫶 <b>Бизнес улучшен на {enchanced} уровней.</b>")
