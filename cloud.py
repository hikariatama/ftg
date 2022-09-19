#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://static.hikari.gay/cloud_icon.png
# meta banner: https://mods.hikariatama.ru/badges/cloud.jpg
# meta developer: @hikarimods
# scope: hikka_only
# scope: hikka_min 1.2.10

import difflib
import inspect
import io
import time
import contextlib

import requests
import telethon
from telethon.tl.types import Message

from .. import loader, utils


@loader.tds
class ModuleCloudMod(loader.Module):
    """Hikari modules management"""

    strings = {
        "name": "ModuleCloud",
        "args": "🚫 <b>Args not specified</b>",
        "mod404": "🚫 <b>Module {} not found</b>",
        "ilink": (
            "💻 <b><u>{name}</u> - <a"
            ' href="https://mods.hikariatama.ru/view/{file}.py">source</a></b>\nℹ️'
            " <i>{desc}</i>\n\n<i>By @hikarimods with 💗</i>\n\n🌘 <code>.dlmod"
            " {file}</code>"
        ),
        "404": "😔 <b>Module not found</b>",
        "not_exact": (
            "⚠️ <b>No exact match occured, so the closest result is shown instead</b>"
        ),
    }

    strings_ru = {
        "args": "🚫 <b>Нет аргументов</b>",
        "mod404": "🚫 <b>Модуль {} не найден</b>",
        "_cmd_doc_addmod": (
            "<файл> - Отправить модуль в @hikka_talks для добавления в базу"
        ),
        "_cmd_doc_ilink": "<modname> - Получить баннер модуля Хикари",
        "_cls_doc": "Поиск и предложение модулей в HikariMods Database",
        "not_exact": (
            "⚠️ <b>Точного совпадения не нашлось, поэтому был выбран наиболее"
            " подходящее</b>"
        ),
    }

    async def search(self, entity, message: Message):
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
    async def ilinkcmd(self, message: Message):
        """<modname> - Get hikari module banner"""
        args = utils.get_args_raw(message)

        badge = await utils.run_sync(
            requests.get, f"https://mods.hikariatama.ru/badge/{args}"
        )

        if badge.status_code == 404:
            await utils.answer(message, self.strings("mod404").format(args))
            return

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
                else (
                    f'📼 <b><a href="{link}">Link</a> for'
                    f" {utils.escape_html(class_name)}:</b>"
                    f' <code>{link}</code>\n\n{self.strings("not_exact") if not exact else ""}'
                )
            )

            file = io.BytesIO(sys_module.__loader__.data)
            file.name = f"{class_name}.py"
            file.seek(0)

            await message.respond(text, file=file)

            if message.out:
                await message.delete()
        except Exception:
            await utils.answer(message, self.strings("404"))
