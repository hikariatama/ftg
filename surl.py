#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# scope: hikka_min 1.2.10

# meta pic: https://img.icons8.com/external-xnimrodx-lineal-color-xnimrodx/512/000000/external-short-shopping-mall-xnimrodx-lineal-color-xnimrodx.png
# meta developer: @hikarimods
# scope: hikka_only

import logging

import requests
from telethon.tl.types import Message, MessageEntityUrl

from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class AutoShortenerMod(loader.Module):
    """Automatically shortens urls in your messages, which are larger than specified threshold"""

    strings = {
        "name": "AutoShortener",
        "state": "🔗 <b>Auotmatic url shortener is now {}</b>",
        "no_args": "🔗 <b>No link to shorten</b>",
    }

    strings_ru = {
        "state": "🔗 <b>Автоматический сократитель ссылок теперь {}</b>",
        "no_args": "🔗 <b>Не указана ссылка для сокращения</b>",
        "_cmd_doc_autosurl": "Включить\\выключить автоматическое сокращение ссылок",
        "_cmd_doc_surl": "[ссылка] [движок]- Сократить ссылку",
        "_cls_doc": (
            "Автоматически сокращает ссылки в твоих сообщениях, если они длиннее"
            " значения в конфиге"
        ),
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "threshold",
                80,
                lambda: "Urls larger than this value will be automatically shortened",
                validator=loader.validators.Integer(minimum=50),
            ),
            loader.ConfigValue(
                "auto_engine",
                "owo",
                lambda: "Engine to auto-shorten urls with",
                validator=loader.validators.Choice(["owo", "gg", "gay"]),
            ),
        )

    async def autosurlcmd(self, message: Message):
        """Toggle automatic url shortener"""
        state = not self.get("state", False)
        self.set("state", state)
        await utils.answer(
            message, self.strings("state").format("on" if state else "off")
        )

    async def surlcmd(self, message: Message):
        """[url] [engine]- Shorten url"""
        if (
            not getattr(message, "raw_text", False)
            or not getattr(message, "entities", False)
            or not message.entities
            or not any(
                isinstance(entity, MessageEntityUrl) for entity in message.entities
            )
        ):
            reply = await message.get_reply_message()
            if (
                not reply
                or not getattr(reply, "raw_text", False)
                or not getattr(reply, "entities", False)
                or not reply.entities
                or not any(
                    isinstance(entity, MessageEntityUrl) for entity in reply.entities
                )
            ):
                await utils.answer(message, self.strings("no_args"))
                return

            txt = reply.raw_text
            text = reply.text
            entities = reply.entities
            just_url = False
        else:
            txt = message.raw_text
            text = message.text
            entities = message.entities
            just_url = True

        urls = [
            txt[entity.offset : entity.offset + entity.length] for entity in entities
        ]

        if just_url:
            text = ""

        for url in urls:
            surl = await self.shorten(
                url, txt.split()[-1] if len(txt.split()) > 1 else None
            )
            if not just_url:
                text = text.replace(url, surl)
            else:
                text += f"{surl} | "

        await utils.answer(message, text.strip(" | "))

    @staticmethod
    async def shorten(url, engine=None) -> str:
        if not engine or engine == "gg":
            r = await utils.run_sync(
                requests.post,
                "http://gg.gg/create",
                data={
                    "custom_path": None,
                    "use_norefs": 0,
                    "long_url": url,
                    "app": "site",
                    "version": "0.1",
                },
            )

            return r.text
        elif engine in ["owo", "gay"]:
            r = await utils.run_sync(
                requests.post,
                "https://owo.vc/generate",
                json={
                    "link": url,
                    "generator": engine,
                    "preventScrape": True,
                    "owoify": True,
                },
                headers={"User-Agent": "https://mods.hikariatama.ru/view/surl.py"},
            )

            logger.debug(r.json())

            return "https://" + r.json()["result"]

    async def watcher(self, message: Message):
        if (
            not getattr(message, "text", False)
            or not getattr(message, "out", False)
            or not getattr(message, "entities", False)
            or not message.entities
            or not any(
                isinstance(entity, MessageEntityUrl) for entity in message.entities
            )
            or not self.get("state", False)
            or message.raw_text.lower().startswith(self.get_prefix())
        ):
            return

        entities = message.entities
        urls = list(
            filter(
                lambda x: len(x) > int(self.config["threshold"]),
                [
                    message.raw_text[entity.offset : entity.offset + entity.length]
                    for entity in entities
                ],
            )
        )

        if not urls:
            return

        text = message.text

        for url in urls:
            text = text.replace(
                url, await self.shorten(url, self.config["auto_engine"])
            )

        await message.edit(text)
