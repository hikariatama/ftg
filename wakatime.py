__version__ = (2, 0, 0)

#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html
# Updated by a https://t.me/vsecoder

# meta pic: https://static.hikari.gay/wakatime_icon.png
# meta banner: https://mods.hikariatama.ru/badges/wakatime.jpg
# meta developer: @hikarimods
# inspiration: @vsecoder
# requires: aiohttp
# scope: inline
# scope: hikka_only
# scope: hikka_min 1.2.10

import asyncio
import logging
import json

import aiohttp
from telethon.errors.rpcerrorlist import FloodWaitError, MessageNotModifiedError
from telethon.tl.types import Message

from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class WakaTimeMod(loader.Module):
    """WakaTime widget for your @username_bio channels"""

    strings = {
        "name": "WakaTime",
        "state": "🙂 <b>WakaTime widgets are now {}</b>\n{}",
        "error": "<b>WakaTime error</b>\n\n{}",
        "tutorial": (
            "ℹ️ <b>To enable widget, send a message to a preffered chat with text"
            " </b><code>{WAKATIME}</code>"
        ),
        "configuring": "🙂 <b>WakaTime widget is ready and will be updated soon</b>",
        "set_username": (
            "🙂 <b>You need to set your WakaTime username in </b><code>.config</code>"
        ),
    }

    strings_ru = {
        "state": "🙂 <b>Виджеты WakaTime теперь {}</b>\n{}",
        "error": "<b>WakaTime error</b>\n\n{}",
        "tutorial": (
            "ℹ️ <b>Для активации виджета, отправь </b><code>{WAKATIME}</code> <b>в"
            " нужный чат</b>"
        ),
        "configuring": "🙂 <b>Виджет WakaTime готов и скоро будет обновлен</b>",
        "set_username": (
            "🙂 <b>Необходимо установить юзернейм на WakaTime в </b><code>.config</code>"
        ),
        "_cmd_doc_wakaface": "Выбрать эмодзи, которое будет отображаться в виджетах",
        "_cmd_doc_wakatoggle": "Включить\\выключить виджеты",
        "_cls_doc": "Виджеты WakaTime для твоего канала @пользовательname_bio",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "wakatime_username",
                doc=lambda: "Your WakaTime username to parse data from",
            ),
            loader.ConfigValue(
                "update_interval",
                300,
                lambda: "Messages update interval. Not recommended < 300 seconds",
                validator=loader.validators.Integer(minimum=100),
            ),
        )

    async def client_ready(self, client, db):
        self._endpoint = "https://wakatime.com/api/v1/users/{}/stats/last_7_days"

        self.set("widgets", list(map(tuple, self.get("widgets", []))))

        self._task = asyncio.ensure_future(self._parse())

    async def on_unload(self):
        self._task.cancel()

    async def _parse(self, do_not_loop: bool = False):
        while True:
            if not self.config["wakatime_username"] or not self.get("state", False):
                await asyncio.sleep(5)
                continue

            async with aiohttp.ClientSession() as session:
                async with session.request(
                    "GET",
                    self._endpoint.format(self.config["wakatime_username"]),
                ) as resp:
                    r = await resp.text()

            results = json.loads(r)["data"]

            for widget in self.get("widgets", []):
                try:
                    await self._client.edit_message(
                        *widget[:2],
                        self._format(
                            results,
                            widget[2] if len(widget) > 2 else "{WAKATIME}",
                        ),
                    )
                except MessageNotModifiedError:
                    pass
                except FloodWaitError:
                    pass
                except Exception:
                    logger.debug("Wakatime widget update failed")
                    self.set(
                        "widgets", list(set(self.get("widgets", [])) - set([widget]))
                    )
                    continue

            if do_not_loop:
                break

            await asyncio.sleep(int(self.config["update_interval"]))

    def _format(self, stats: list, template: str) -> str:
        return template.format(
            WAKATIME="\n".join(
                [
                    f" ▫️ <b>{stat['name']}</b>: <i>{stat['text']}</i>"
                    for stat in stats["languages"]
                    if stat["text"] != "0 secs"
                ]
            )
        )

    async def wakatogglecmd(self, message: Message):
        """Toggle widgets' updates"""
        if not self.config["wakatime_username"]:
            await utils.answer(message, self.strings("set_username"))
            return

        state = not self.get("state", False)
        self.set("state", state)
        await utils.answer(
            message,
            self.strings("state").format(
                "on" if state else "off", self.strings("tutorial") if state else ""
            ),
        )

    async def watcher(self, message: Message):
        try:
            if "{WAKATIME}" not in getattr(message, "text", "") or not message.out:
                return

            chat_id = utils.get_chat_id(message)
            message_id = message.id

            self.set(
                "widgets",
                self.get("widgets", []) + [(chat_id, message_id, message.text)],
            )

            await utils.answer(message, self.strings("configuring"))
            await self._parse(do_not_loop=True)
        except Exception as e:
            logger.exception("Can't send widget")
            await utils.answer(message, self.strings("error").format(e))
