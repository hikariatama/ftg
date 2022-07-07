#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://img.icons8.com/fluency/240/000000/archive.png
# meta developer: @hikarimods

import asyncio
import io

import requests
from telethon.tl.types import Message

from .. import loader, utils


@loader.tds
class Web2fileMod(loader.Module):
    """Download content from link and send it as file"""

    strings = {
        "name": "Web2file",
        "no_args": "🚫 <b>Specify link</b>",
        "fetch_error": "🚫 <b>Download error</b>",
        "loading": "🦊 <b>Downloading...</b>",
    }

    strings_ru = {
        "no_args": "🚫 <b>Укажи ссылку</b>",
        "fetch_error": "🚫 <b>Ошибка загрузки</b>",
        "loading": "🦊 <b>Загрузка...</b>",
        "_cls_doc": "Скачивает содержимое ссылки и отправляет в виде файла",
    }

    async def on_unload(self):
        asyncio.ensure_future(
            self._client.inline_query("@hikkamods_bot", "#statunload:web2file")
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

        self.allmodules._hikari_stats += ["web2file"]

        if not hasattr(self.allmodules, "_hikari_stats_task"):
            self.allmodules._hikari_stats_task = asyncio.ensure_future(
                self.stats_task()
            )

    async def web2filecmd(self, message: Message):
        """Send link content as file"""
        website = utils.get_args_raw(message)
        if not website:
            await utils.answer(message, self.strings("no_args", message))
            return
        try:
            f = io.BytesIO(requests.get(website).content)
        except Exception:
            await utils.answer(message, self.strings("fetch_error", message))
            return

        f.name = website.split("/")[-1]

        await message.respond(file=f)
        await message.delete()
