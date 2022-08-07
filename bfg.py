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
            self.set("automining", int(time.time() + 15 * 60))
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

        self.set("automining", int(time.time() + 60 * 60))
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

        self.set("automining_sell", int(time.time() + 30 * 60))


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


class Poisons:
    async def _create_poisons(self):
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
class BFGMod(loader.Module, Mining, Bonuses, Poisons):
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
                "autopoisons",
                True,
                "Автоматически варить зелья",
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
            message = await self._get_msg("garden")

            await message.click(data=b"payTaxesGarden")
            await asyncio.sleep(1)
            await message.click(data=b"pourGarden")
            await asyncio.sleep(1)
            await message.click(data=b"collectIncomeGarden")
            self.set("garden_time", int(time.time() + 60 * 60))
            return True
        except Exception:
            self.set("garden_time", int(time.time() + 5 * 60))
            self.set("garden", f"exp/{time.time() + 5 * 60:.0f}")
            return False

    async def _generator(self) -> bool:
        try:
            message = await self._get_msg("generator")

            await message.click(data=b"payTaxesGenerator")
            await asyncio.sleep(1)
            await message.click(data=b"collectIncomeGenerator")
            self.set("generator_time", int(time.time() + 60 * 60))
            return True
        except Exception:
            self.set("generator_time", int(time.time() + 5 * 60))
            self.set("generator", f"exp/{time.time() + 5 * 60:.0f}")
            return False

    async def _business(self) -> bool:
        try:
            message = await self._get_msg("business")

            await message.click(data=b"payTaxes")
            await asyncio.sleep(1)
            await message.click(data=b"collectIncome")
            self.set("business_time", int(time.time() + 60 * 60))
            return True
        except Exception:
            self.set("business_time", int(time.time() + 5 * 60))
            self.set("business", f"exp/{time.time() + 5 * 60:.0f}")
            return False

    async def _farm(self) -> bool:
        try:
            message = await self._get_msg("farm")

            await message.click(data=b"payTaxesFarm")
            await asyncio.sleep(1)
            await message.click(data=b"collectIncomeFarm")
            self.set("farm_time", int(time.time() + 60 * 60))
            return True
        except Exception:
            self.set("farm_time", int(time.time() + 5 * 60))
            self.set("farm", f"exp/{time.time() + 5 * 60:.0f}")
            return False

    async def _init(self, key: str, msg: str) -> bool:
        if self.get(key) and (
            not str(self.get(key)).startswith("exp/")
            or int(self.get(key).split("/")[1]) < time.time()
        ):
            return True

        async with self._client.conversation(self._bot) as conv:
            await conv.send_message(msg)
            r = await conv.get_response()
            if "чтобы построить введите команду" in r.raw_text:
                self.config[f"auto{key}"] = False
                return False

            self.set(key, f"{utils.get_chat_id(r)}/{r.id}")

        return True

    async def _get_msg(self, key: str) -> Message:
        msg = self.get(key)
        if msg in self._cache:
            return self._cache[msg]

        message = (
            await self._client.get_messages(
                int(msg.split("/")[0]),
                ids=[int(msg.split("/")[1])],
            )
        )[0]

        self._cache[msg] = message
        return message

    @loader.loop(interval=15, autostart=True)
    async def loop(self):
        any_ = False
        if self.config["autopoisons"] and (
            not self.get("poisons") or self.get("poisons") < time.time()
        ):
            await self._create_poisons()
            any_ = True
            await asyncio.sleep(5)

        if (
            self.config["autogarden"]
            and (not self.get("garden_time") or self.get("garden_time") < time.time())
            and await self._init("garden", "Мой сад")
        ):
            await self._garden()
            any_ = True
            await asyncio.sleep(5)

        if (
            self.config["autogenerator"]
            and (
                not self.get("generator_time")
                or self.get("generator_time") < time.time()
            )
            and await self._init("generator", "Мой генератор")
        ):
            await self._generator()
            any_ = True
            await asyncio.sleep(5)

        if (
            self.config["autobusiness"]
            and (
                not self.get("business_time") or self.get("business_time") < time.time()
            )
            and await self._init("business", "Мой бизнес")
        ):
            await self._business()
            any_ = True
            await asyncio.sleep(5)

        if (
            self.config["autofarm"]
            and (not self.get("farm_time") or self.get("farm_time") < time.time())
            and await self._init("farm", "Моя ферма")
        ):
            await self._farm()
            any_ = True
            await asyncio.sleep(5)

        if self.config["automining"]:
            if not self.get("automining") or self.get("automining") < time.time():
                await self._automining()

            if (
                not self.get("automining_sell")
                or self.get("automining_sell") < time.time()
            ):
                await self._mining_sell()

            any_ = True
            await asyncio.sleep(5)

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
