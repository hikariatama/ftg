#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://img.icons8.com/stickers/500/000000/cloud.png
# meta developer: @hikarimods
# requires: hashlib base64

import asyncio
import base64
import difflib
import hashlib
import inspect
import io
import logging
import re
import time
import contextlib

import requests
import telethon
from telethon.tl.types import Message

from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class ModuleCloudMod(loader.Module):
    """Hikari modules management"""

    strings = {
        "name": "ModuleCloud",
        "no_file": "🗿 <b>What should I send?...</b>",
        "cannot_check_file": "🚫 <b>Can't read file...</b>",
        "cannot_join": "🚫 <b>Am I banned in hikari. chat?</b>",
        "args": "🚫 <b>Args not specified</b>",
        "mod404": "🚫 <b>Module {} not found</b>",
        "ilink": '💻 <b><u>{name}</u> - <a href="https://mods.hikariatama.ru/view/{file}.py">source</a></b>\nℹ️ <i>{desc}</i>\n\n<i>By @hikarimods with 💗</i>\n\n🌘 <code>.dlmod {file}</code>',
        "404": "😔 <b>Module not found</b>",
        "not_exact": "⚠️ <b>No exact match occured, so the closest result is shown instead</b>",
    }

    strings_ru = {
        "cannot_check_file": "🚫 <b>Не могу прочитать файл...</b>",
        "cannot_join": "🚫 <b>Может я забанен в чате Хикари?</b>",
        "args": "🚫 <b>Нет аргументов</b>",
        "mod404": "🚫 <b>Модуль {} не найден</b>",
        "_cmd_doc_addmod": "<файл> - Отправить модуль в @hikka_talks для добавления в базу",
        "_cmd_doc_cloud": "<command \\ mod_name> - Поиск модуля в @hikarimods_database",
        "_cmd_doc_imod": "<command \\ mod_name> - Поиск модуля в @hikarimods",
        "_cmd_doc_ilink": "<modname> - Получить баннер модуля Хикари",
        "_cmd_doc_verifmod": "<filename>;<title>;<description>;<tags> - Верифицировать модуль [только для админов @hikarimods]",
        "_cls_doc": "Поиск и предложение модулей в HikariMods Database",
        "not_exact": "⚠️ <b>Точного совпадения не нашлось, поэтому был выбран наиболее подходящее</b>",
    }

    async def on_unload(self):
        asyncio.ensure_future(
            self._client.inline_query("@hikkamods_bot", "#statunload:cloud")
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

        self.allmodules._hikari_stats += ["cloud"]

        if not hasattr(self.allmodules, "_hikari_stats_task"):
            self.allmodules._hikari_stats_task = asyncio.ensure_future(
                self.stats_task()
            )

    async def search(self, entity, message: Message) -> None:
        args = utils.get_args_raw(message)
        try:
            msgs = await self._client.get_messages(entity, limit=100)
        except Exception:
            try:
                await self._client(
                    telethon.tl.functions.channels.JoinChannelRequest(entity)
                )
            except Exception:
                await utils.answer(message, self.strings("cannot_join"))
                return

            msgs = await self._client.get_messages(entity, limit=100)

        for msg in msgs:
            with contextlib.suppress(Exception):
                c = any(
                    word not in msg.raw_text.lower() for word in args.lower().split()
                )
                if not c:
                    await utils.answer(message, msg.text)
                    return

        await utils.answer(message, self.strings("mod404").format(args))

    @loader.unrestricted
    async def cloudcmd(self, message: Message) -> None:
        """<command \\ mod_name> - Lookup mod in @hikarimods_database"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings("args"))
            return

        entity = await self._client.get_entity("@hikarimods_database")
        await self.search(entity, message)

    @loader.unrestricted
    async def imodcmd(self, message: Message) -> None:
        """<command \\ mod_name> - Lookup mod in @hikarimods"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings("args"))
            return

        entity = await self._client.get_entity("@hikarimods")
        await self.search(entity, message)

    @loader.unrestricted
    async def ilinkcmd(self, message: Message) -> None:
        """<modname> - Get hikari module banner"""
        args = utils.get_args_raw(message)

        badge = requests.get(f"https://mods.hikariatama.ru/badge/{args}")

        if badge.status_code == 404:
            return await utils.answer(message, self.strings("mod404").format(args))

        img = requests.get(badge.json()["badge"] + f"?t={round(time.time())}").content
        info = badge.json()["info"]
        info["file"] = info["file"].split(".")[0]

        if not message.media or not message.out:
            await self._client.send_file(
                message.peer_id,
                img,
                caption=self.strings("ilink").format(**info),
            )
            await message.delete()
        else:
            await message.edit(self.strings("ilink").format(**info), file=img)

    async def verifmodcmd(self, message: Message) -> None:
        """<filename>;<title>;<description>;<tags> - Verfiy module [only for @hikarimods admins]"""
        args = utils.get_args_raw(message).split(";")
        filename, title, description, tags = args
        reply = await message.get_reply_message()
        if not reply:
            return

        media = reply.media

        try:
            file = await self._client.download_file(media, bytes)
        except Exception:
            await utils.answer(message, self.strings("no_file"))
            return

        try:
            code = file.decode("utf-8").replace("\r\n", "\n")
        except Exception:
            await utils.answer(message, self.strings("cannot_check_file"))
            await asyncio.sleep(3)
            await message.delete()
            return

        sha1 = hashlib.sha1()
        sha1.update(code.encode("utf-8"))
        file_hash = str(sha1.hexdigest())
        open("/home/ftg/verified_mods.db", "a").write(file_hash + "\n")
        if "hikarimods" in tags:
            url = f"https://github.com/hikariatama/ftg/raw/master/{filename}"
        else:
            encoded_string = base64.b64encode(file)
            stout = encoded_string.decode("utf-8")
            TOKEN = open("/home/ftg/git.token", "r").read()
            url = f"https://api.github.com/repos/hikariatama/host/contents/{filename}"
            head = {
                "Authorization": f"token {TOKEN}",
                "Accept": "application/vnd.github.v3+json",
            }
            git_data = '{"message": "Upload file", "content":' + '"' + stout + '"' + "}"
            requests.put(url, headers=head, data=git_data)
            url = f"https://github.com/hikariatama/host/raw/master/{filename}"

        commands = "".join(
            f"<code>.{command}" + "</code>\n"
            for command in re.findall(r"[\n][ \t]+async def ([^\(]*?)cmd", code)
        )

        await utils.answer(
            message,
            "<b>👾 Module verified and can be found in @hikarimods_database</b>",
        )
        await self._client.send_message(
            "t.me/hikarimods_database",
            f"🦊 <b><u>{title}</u></b>\n<i>{description}</i>\n\n📋 <b><u>Команды:</u></b>\n{commands}\n🚀 <code>.dlmod {url}</code>\n\n#"
            + " #".join(tags.split(",")),
        )

    async def mlcmd(self, message: Message):
        """<module name> - Send link to module"""
        args = utils.get_args_raw(message)
        exact = True
        if not args:
            await utils.answer(message, "🚫 <b>No args</b>")
            return

        try:
            try:
                class_name = next(
                    module.strings["name"]
                    for module in self.allmodules.modules
                    if args.lower() == module.strings["name"].lower()
                )
            except Exception:
                try:
                    class_name = next(
                        reversed(
                            sorted(
                                [
                                    module.strings["name"]
                                    for module in self.allmodules.modules
                                ],
                                key=lambda x: difflib.SequenceMatcher(
                                    None,
                                    args.lower(),
                                    x,
                                ).ratio(),
                            )
                        )
                    )
                    exact = False
                except Exception:
                    await utils.answer(message, self.strings("404"))
                    return

            module = next(
                filter(
                    lambda mod: class_name.lower() == mod.strings["name"].lower(),
                    self.allmodules.modules,
                )
            )

            sys_module = inspect.getmodule(module)

            link = module.__origin__

            text = (
                f"<b>🧳 {utils.escape_html(class_name)}</b>"
                if not utils.check_url(link)
                else f'📼 <b><a href="{link}">Link</a> for {utils.escape_html(class_name)}:</b> <code>{link}</code>\n\n{self.strings("not_exact") if not exact else ""}'
            )

            file = io.BytesIO(sys_module.__loader__.data)
            file.name = f"{class_name}.py"
            file.seek(0)

            await message.respond(text, file=file)

            if message.out:
                await message.delete()
        except Exception:
            raise
            await utils.answer(message, self.strings("404"))
