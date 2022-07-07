#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://img.icons8.com/external-flaticons-lineal-color-flat-icons/512/000000/external-sleep-productivity-flaticons-lineal-color-flat-icons.png
# meta developer: @hikarimods
# scope: hikka_only

import asyncio
import re
import time

from telethon.tl.types import Message

from .. import loader, utils


def s2time(temp_time: str) -> int:
    seconds, minutes, hours = 0, 0, 0

    try:
        seconds = int(str(re.search("([0-9]+)s", temp_time).group(1)))
    except Exception:
        pass

    try:
        minutes = int(str(re.search("([0-9]+)m", temp_time).group(1))) * 60
    except Exception:
        pass

    try:
        hours = int(str(re.search("([0-9]+)h", temp_time).group(1))) * 60 * 60
    except Exception:
        pass

    return round(seconds + minutes + hours)


@loader.tds
class YouDBetterSleepMod(loader.Module):
    """Restricts user from sending messages while sleeping"""

    strings = {
        "name": "YouDBetterSleep",
        "no_time": "🚫 <b>You can't sleep forever, specify <time> argument</b>",
        "awake": "🥱 <b>Good morning</b>",
        "asleep": "😴 <b>Good night. Now I can't write messages for {}</b>",
        "disabled": "😴 <b>I can't write messages, because my userbot wants me to sleep</b>",
    }

    strings_ru = {
        "no_time": "👾 <b>Ты не можешь спать вечно, укажи аргумент <время></b>",
        "awake": "🥱 <b>Доброе утро</b>",
        "asleep": "😴 <b>Спокойной ночи. Я не могу писать сообщения на протяжении {}</b>",
        "disabled": "😴 <b>Я не могу писать сообщения, так как мой юзербот хочет, чтобы я поспал</b>",
        "_cmd_doc_sleep": "<время> - Время сна",
        "_cls_doc": "Запрещает писать во время сна",
    }

    async def on_unload(self):
        asyncio.ensure_future(
            self._client.inline_query("@hikkamods_bot", "#statunload:youdbettersleep")
        )

    async def stats_task(self):
        await asyncio.sleep(60)
        await self._client.inline_query(
            "@hikkamods_bot",
            f"#statload:{','.join(list(set(self.allmodules._hikari_stats)))}",
        )
        delattr(self.allmodules, "_hikari_stats")
        delattr(self.allmodules, "_hikari_stats_task")

    async def client_ready(self, client, db):
        self._db = db
        self._client = client

        if not hasattr(self.allmodules, "_hikari_stats"):
            self.allmodules._hikari_stats = []

        self.allmodules._hikari_stats += ["youdbettersleep"]

        if not hasattr(self.allmodules, "_hikari_stats_task"):
            self.allmodules._hikari_stats_task = asyncio.ensure_future(
                self.stats_task()
            )

    @loader.sudo
    async def sleepcmd(self, message: Message):
        """<time> - Sleep for time"""
        args = utils.get_args_raw(message)

        t = s2time(args)

        if not args or t == 0:
            self.set("asleep", False)
            self.get("until", 0)
            await utils.answer(message, self.strings("awake"))
        else:
            self.set("asleep", True)
            self.set("until", t + time.time())
            await utils.answer(message, self.strings("asleep").format(args))

    async def watcher(self, message: Message):
        if (
            not isinstance(message, Message)
            or not hasattr(message, "text")
            or not self.get("asleep", False)
            or not self.get("until", False)
            or message.text == f"{self.get_prefix()}sleep"
        ):
            return

        if self.get("until", 0) <= time.time():
            self.set("until", 0)
            self.set("asleep", False)
            await self.inline.bot.send_message(
                self._tg_id,
                self.strings("awake"),
                parse_mode="HTML",
            )
            return

        if message.mentioned:
            await self._client.send_read_acknowledge(
                message.peer_id,
                message,
                clear_mentions=True,
            )
            await utils.answer(message, self.strings("disabled"))

        if not message.out:
            return

        await utils.answer(message, self.strings("disabled"))
