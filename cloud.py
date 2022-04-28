# █ █ ▀ █▄▀ ▄▀█ █▀█ ▀    ▄▀█ ▀█▀ ▄▀█ █▀▄▀█ ▄▀█
# █▀█ █ █ █ █▀█ █▀▄ █ ▄  █▀█  █  █▀█ █ ▀ █ █▀█
#
#              © Copyright 2022
#
#          https://t.me/hikariatama
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://img.icons8.com/fluency/48/000000/cloud-storage.png
# meta developer: @hikariatama
# requires: hashlib base64

from .. import loader, utils
import asyncio
import re
import requests
import telethon
import hashlib
import base64
from telethon.tl.types import Message
import inspect
import io
import difflib
import logging

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
        "ilink": '<b><u>{name}</u> - <a href="https://mods.hikariatama.ru/view/{file}">source</a></b> | <i>By @hikarimods with ❤️‍🩹</i>\nℹ️ <i>{desc}</i>\n{hikka_only}\n🌃 <b>Install:</b> <code>.dlmod https://mods.hikariatama.ru/{file}</code>',
        "hikka_only": "\n🌘 <b><u>Hikka</u> only</b>\n",
        "404": "😔 <b>Module not found</b>"
    }

    async def client_ready(self, client, db):
        self._db = db
        self._client = client

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
                await utils.answer(message, self.strings("cannot_join", message))
                return

            msgs = await self._client.get_messages(entity, limit=100)

        for msg in msgs:
            try:
                c = any(
                    word not in msg.raw_text.lower() for word in args.lower().split()
                )
                if not c:
                    await utils.answer(message, msg.text)
                    return
            except Exception:  # Ignore errors when trying to get text of e.g. service message
                pass

        await utils.answer(message, self.strings("mod404", message).format(args))

    @loader.unrestricted
    async def cloudcmd(self, message: Message) -> None:
        """<command \\ mod_name> - Lookup mod in @hikarimods_database"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings("args", message))
            return

        entity = await self._client.get_entity("@hikarimods_database")
        await self.search(entity, message)

    @loader.unrestricted
    async def imodcmd(self, message: Message) -> None:
        """<command \\ mod_name> - Lookup mod in @hikarimods"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings("args", message))
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

        img = requests.get(badge.json()["badge"]).content
        info = badge.json()["info"]

        hikka_only = self.strings("hikka_only") if info["hikka_only"] else ""
        del info["hikka_only"]

        if not message.media or not message.out:
            await self._client.send_file(
                message.peer_id,
                img,
                caption=self.strings("ilink").format(hikka_only=hikka_only, **info),
            )
            await message.delete()
        else:
            await message.edit(
                self.strings("ilink").format(hikka_only=hikka_only, **info), file=img
            )

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
            await utils.answer(message, self.strings("no_file", message))
            return

        try:
            code = file.decode("utf-8").replace("\r\n", "\n")
        except Exception:
            await utils.answer(message, self.strings("cannot_check_file", message))
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
                else f'📼 <b><a href="{link}">Link</a> for {utils.escape_html(class_name)}:</b> <code>{link}</code>'
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
