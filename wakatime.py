# █ █ ▀ █▄▀ ▄▀█ █▀█ ▀    ▄▀█ ▀█▀ ▄▀█ █▀▄▀█ ▄▀█
# █▀█ █ █ █ █▀█ █▀▄ █ ▄  █▀█  █  █▀█ █ ▀ █ █▀█
#
#              © Copyright 2022
#
#          https://t.me/hikariatama
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://img.icons8.com/color/480/000000/wakanim.png
# meta developer: @hikariatama
# scope: inline
# scope: hikka_only
# scope: hikka_min 1.1.14
# requires: aiohttp

import asyncio
import logging
import re

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
        "tutorial": "ℹ️ <b>To enable widget, send a message to a preffered chat with text </b><code>{WAKATIME}</code>",
        "configuring": "🙂 <b>WakaTime widget is ready and will be updated soon</b>",
        "set_username": "🙂 <b>You need to set your WakaTime username in </b><code>.config</code>",
    }

    strings_ru = {
        "state": "🙂 <b>Виджеты WakaTime теперь {}</b>\n{}",
        "tutorial": "ℹ️ <b>Для активации виджета, отправь </b><code>{WAKATIME}</code> <b>в нужный чат</b>",
        "configuring": "🙂 <b>Виджет WakaTime готов и скоро будет обновлен</b>",
        "set_username": "🙂 <b>Необходимо установить юзернейм на WakaTime в </b><code>.config</code>",
        "_cmd_doc_wakaface": "Выбрать эмодзи, которое будет отображаться в виджетах",
        "_cmd_doc_wakatoggle": "Включить\\выключить виджеты",
        "_cls_doc": "Виджеты WakaTime для твоего канала @пользовательname_bio",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "wakatime_username",
                "",
                lambda: "Your WakaTime username to parse data from",
            ),
            loader.ConfigValue(
                "update_interval",
                300,
                lambda: "Messages update interval. Not recommended < 300 seconds",
            ),
        )

    async def client_ready(self, client, db):
        self._db = db
        self._client = client
        self._endpoint = "https://github-readme-stats.vercel.app/api/wakatime?username={}&show_icons=false&hide_progress=true&layout=true"

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
                    "GET", self._endpoint.format(self.config["wakatime_username"])
                ) as resp:
                    r = await resp.text()

            r = r.replace(" ", "").replace("\n", "")
            results = [
                (
                    i[0],
                    int(re.sub(r"[^\d]", "", i[1])) if i[1] else 0,
                    int(re.sub(r"[^\d]", "", i[2])) if i[2] else 0,
                )
                for i in re.findall(
                    r'<textclass.*?data-testid=".*?>(.*?):<\/text><textclass="stat".*?>(\d+hrs)?(\d+mins)<\/text>',
                    r,
                )
            ]

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
                    logger.exception("Wakatime widget update failed")
                    self.set(
                        "widgets", list(set(self.get("widgets", [])) - set([widget]))
                    )
                    continue

            if do_not_loop:
                break

            await asyncio.sleep(int(self.config["update_interval"]))

    def _format(self, stats: list, template: str) -> str:
        result = ""
        for stat in stats:
            hrs = f"{stat[1]} hrs " if stat[1] else ""
            mins = f"{stat[2]} mins" if stat[2] else ""
            result += f"▫️ <b>{stat[0]}</b>: <i>{hrs}{mins}</i>\n"

        return template.format(WAKATIME=result)

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
        if "{WAKATIME}" not in getattr(message, "text", "") or not message.out:
            return

        chat_id = utils.get_chat_id(message)
        message_id = message.id

        self.set(
            "widgets", self.get("widgets", []) + [(chat_id, message_id, message.text)]
        )

        await utils.answer(message, self.strings("configuring"))
        await self._parse(do_not_loop=True)
