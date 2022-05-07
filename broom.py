# █ █ ▀ █▄▀ ▄▀█ █▀█ ▀    ▄▀█ ▀█▀ ▄▀█ █▀▄▀█ ▄▀█
# █▀█ █ █ █ █▀█ █▀▄ █ ▄  █▀█  █  █▀█ █ ▀ █ █▀█
#
#              © Copyright 2022
#
#          https://t.me/hikariatama
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://img.icons8.com/external-icongeek26-flat-icongeek26/512/000000/external-broom-magic-and-fairy-tale-icongeek26-flat-icongeek26.png
# meta developer: @hikariatama
# scope: hikka_only

import asyncio
import json
import re

import requests
from telethon.tl.functions.contacts import BlockRequest
from telethon.tl.functions.messages import DeleteHistoryRequest
from telethon.tl.types import Message, User

from .. import loader, utils


@loader.tds
class MagicBroomMod(loader.Module):
    """Magic broom that cleans database and chats"""

    strings = {
        "name": "MagicBroom",
        "no_args": "🚫 <b>Args are mandatory </b><code>.help MagicBroom</code>",
        "will_be_removed": "<b>✅ {} dialogs will be deleted:</b>\n<pre>   🔸 {}</pre>\n\n🔰 Use: <code>.broom {}</code>",
        "nothing_will_be_removed": "<b>✅ No chats will be deleted</b>",
        "fuck_off": "🦊 <b>I don't wanna any messages from you, ergo you are banned.</b>",
        "removed": "<b>✅ {} dialogs deleted:</b>\n<pre>   🔸 {}</pre>",
        "nothing_removed": "<b>✅ No chats have been deleted</b>",
        "broom_file": "\n✅ Removed {} filemods",
        "broom_deadrepos": "\n✅ Removed {} dead repos",
        "broom_refactorrepos": "\n✅ Replaced {} old repos",
        "broom_deletedconfs": "\n✅ Removed {} unloaded mod configs",
        "processing": "<b>🦊 Processing...</b>",
        "result": "<b>🦊 Result:</b>\n",
    }

    strings_ru = {
        "no_args": "🚫 <b>Аргументы обязательны, смотри </b><code>.help MagicBroom</code>",
        "will_be_removed": "<b>✅ {} диалогов будет удалено:</b>\n<pre>   🔸 {}</pre>\n\n🔰 Команда: <code>.broom {}</code>",
        "nothing_will_be_removed": "<b>✅ Не будет удалено ни одного чата</b>",
        "fuck_off": "🦊 <b>Я не хочу никаких сообщений от тебя, поэтому ты заблокирован.</b>",
        "removed": "<b>✅ {} диалогов удалено:</b>\n<pre>   🔸 {}</pre>",
        "nothing_removed": "<b>✅ Не было удалено ни одного чата</b>",
        "broom_file": "\n✅ Удалено {} файловых модулей",
        "broom_deadrepos": "\n✅ Удалено {} мертвых репо",
        "broom_refactorrepos": "\n✅ Заменил {} старых репо",
        "broom_deletedconfs": "\n✅ Удалено {} конфигов выгруженных модулей",
        "processing": "<b>🦊 Обработка...</b>",
        "result": "<b>🦊 Результат:</b>\n",
        "_cmd_doc_broomp": "<args> - Препросмотр .broom",
        "_cmd_doc_broom": "<args> - Волшебная метла\n-d - Удалить диалоги с удаленными аккаунтами\n-b - Удалить диалоги с заблокированными аккаунтами\n-s - Удалить диалоги со скам аккаунтами\n-q <запрос> - Поиск запроса и удаление диалогов, соответствующих ему",
        "_cmd_doc_washdb": "<arg> - Очистка базы данных (рекомендуется .backupdb)\n-1 --filemods - Удалить конфиги модулей, загруженных из файла\n-2 --deadrepos - Удалить мертвые репо\n-3 --refactorrepos - Заменить страшные ссылки репозиториев на нормальные\n-4 --deleteconf - Удалить конфиги выгруженных модулей\n-a --all - Применить все фильтры выше",
        "_cmd_doc_pban": "<args> - Избавиться от чата\n-h - Очистить историю для себя\n-hh - Очистить историю для всех",
        "_cls_doc": "Волшебная метла очистит базу данных и диалоги от хлама",
    }

    async def client_ready(self, client, db):
        self._db = db
        self._client = client

    async def broom(self, message: Message) -> False or list:
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings("no_args", message))
            await asyncio.sleep(3)
            await message.delete()
            return False

        deleted, restricted, scam, query = False, False, False, False

        if "-d" in args:
            args = args.replace("-d", "").replace("  ", " ")
            deleted = True

        if "-b" in args:
            args = args.replace("-b", "").replace("  ", " ")
            restricted = True

        if "-s" in args:
            args = args.replace("-s", "").replace("  ", " ")
            scam = True

        if "-q" in args:
            query = re.search(r'-q [\'"]?([^ ]*)[\'"]?', args).group(1)

        dialogs = await self._client.get_dialogs()
        todel = []
        for dialog in dialogs:
            if "hikka" in dialog.name.lower():
                continue

            if (
                scam
                and getattr(dialog.entity, "scam", False)
                or restricted
                and getattr(dialog.entity, "restricted", False)
                or deleted
                and getattr(dialog.entity, "deleted", False)
                or query
                and (
                    query.lower() in dialog.name.lower()
                    or re.match(query, dialog.name) is not None
                )
            ):
                todel.append(dialog)

        return todel

    async def broompcmd(self, message: Message):
        """<args> - Dry mode of broom"""
        ans = await self.broom(message)
        if ans is False:
            return
        if len(ans) > 0:
            chats = "\n   🔸 ".join([d.name for d in ans])
            await utils.answer(
                message,
                self.strings("will_be_removed", message).format(
                    len(ans), chats, message.text[7:]
                ),
            )
        else:
            await utils.answer(
                message, self.strings("nothing_will_be_removed", message)
            )

    async def broomcmd(self, message):
        """<args> - Magic broom
        -d - Remove dialogs with deleted accounts
        -b - Remove dialogs with banned accounts
        -s - Remove dialogs with scam accounts
        -q <query> - Search query and remove this dialogs"""
        ans = await self.broom(message)
        if ans is False:
            return

        [await self._client.delete_dialog(d.entity) for d in ans]

        if len(ans) > 0:
            chats = "\n   🔸 ".join([d.name for d in ans])
            await utils.answer(
                message, self.strings("removed", message).format(len(ans), chats)
            )
        else:
            await utils.answer(message, self.strings("nothing_removed", message))

    async def washdbcmd(self, message):
        """<arg> - Clean database (.backupdb recommended)
        -1 --filemods - Remove filemod configs
        -2 --deadrepos - Remove dead repos
        -3 --refactorrepos - Repalce githubusercontent links
        -4 --deleteconf - Remove unloaded mod configs
        -a --all - Apply all filters below"""
        args = utils.get_args_raw(message)
        await utils.answer(message, self.strings("processing", message))

        if "-a" in args or "--all" in args:
            args = "-1 -2 -3 -4"

        res = self.strings("result")

        if "--filemods" in args or "-1" in args:
            todel = [x for x in self._db.keys() if "__extmod" in x or "filemod_" in x]
            for delete in todel:
                self._db.pop(delete)

            res += self.strings("broom_file", message).format(len(todel))

        if "--deadrepos" in args or "-2" in args:
            counter = 0
            mods = []
            for mod in self._db.get("hikka.modules.loader", "loaded_modules"):
                if ("http://" in mod or "https://" in mod) and requests.get(
                    mod
                ).status_code == 404:
                    counter += 1
                else:
                    mods.append(mod)

            self._db.set("hikka.modules.loader", "loaded_modules", mods)
            res += self.strings("broom_deadrepos", message).format(counter)

        if "--refactorrepos" in args or "-3" in args:
            counter = json.dumps(self._db).count("githubusercontent")
            mods = re.sub(
                r"http[s]?:\/\/raw\.githubusercontent\.com\/([^\/]*?\/[^\/]*?)(\/[^\"\']*)",
                r"https://github.com/\1/raw\2",
                re.sub(
                    r"http[s]?:\/\/raw%dgithubusercontent%dcom\/([^\/]*?\/[^\/]*?)(\/[^\"\']*)",
                    r"https://github%dcom/\1/raw\2",
                    json.dumps(self._db),
                    flags=re.S,
                ),
                flags=re.S,
            )
            self._db.clear()
            self._db.update(**json.loads(mods))

            res += self.strings("broom_refactorrepos", message).format(counter)

        if "--deleteconf" in args or "-4" in args:
            todel = []
            for x in self._db.keys():
                if x.startswith("hikka.modules."):
                    link = x.split(".", 3)[2].replace("%d", ".")
                    if (
                        link
                        not in self._db.get("hikka.modules.loader", "loaded_modules")
                        and link != "loader"
                    ):
                        todel.append(x)

            for delete in todel:
                self._db.pop(delete)

            res += self.strings("broom_deletedconfs", message).format(len(todel))

        if res == self.strings("result"):
            res += "Nothing's changed"

        self._db.save()
        await utils.answer(message, res)

    async def pbancmd(self, message):
        """<args> - Get off the chat
        -h - Clear history
        -hh - Clear history for both members"""
        args = utils.get_args_raw(message)
        entity = await self._client.get_entity(message.peer_id)
        if not isinstance(entity, User):
            await self._client.delete_dialog(entity)
            return

        try:
            if "-hh" in args:
                await self._client(
                    DeleteHistoryRequest(
                        peer=entity, just_clear=False, revoke=True, max_id=0
                    )
                )
            elif "-h" in args:
                await self._client(
                    DeleteHistoryRequest(peer=entity, just_clear=True, max_id=0)
                )
                await self._client.send_message(
                    utils.get_chat_id(message), self.strings("fuck_off", message)
                )
            else:
                await self._client.send_message(
                    utils.get_chat_id(message), self.strings("fuck_off", message)
                )
        except Exception:
            pass

        await self._client(BlockRequest(id=entity))
