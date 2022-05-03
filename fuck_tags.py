# █ █ ▀ █▄▀ ▄▀█ █▀█ ▀    ▄▀█ ▀█▀ ▄▀█ █▀▄▀█ ▄▀█
# █▀█ █ █ █ █▀█ █▀▄ █ ▄  █▀█  █  █▀█ █ ▀ █ █▀█
#
#              © Copyright 2022
#
#          https://t.me/hikariatama
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://img.icons8.com/fluency/48/000000/radio-waves.png
# meta developer: @hikariatama
# scope: hikka_only

from .. import loader, utils
import asyncio
from telethon.tl.types import Message


@loader.tds
class FuckTagsMod(loader.Module):
    """Auto-read tags and messages in selected chats"""

    strings = {
        "name": "FuckTags",
        "args": "🚫 <b>Incorrect args specified</b>",
        "on": "✅ <b>Now I ignore tags in this chat</b>",
        "off": "✅ <b>Now I don't ignore tags in this chat</b>",
        "on_strict": "✅ <b>Now I automatically read messages in this chat</b>",
        "off_strict": "✅ <b>Now I don't automatically read messages in this chat</b>",
        "do_not_tag_me": "🦊 <b>Please, do not tag me.</b>",
    }

    strings_ru = {
        "args": "🚫 <b>Указаны неверные аргументы</b>",
        "on": "✅ <b>Теперь я буду игнорировать теги в этом чате</b>",
        "off": "✅ <b>Теперь я не буду игнорировать теги в этом чате</b>",
        "on_strict": "✅ <b>Теперь я буду автоматически читать сообщения в этом чате</b>",
        "off_strict": "✅ <b>Теперь я не буду автоматически читать сообщения в этом чате</b>",
        "do_not_tag_me": "🦊 <b>Пожалуйста, не тегайте меня.</b>",
        "_cmd_doc_fucktags": "[чат] - Включить\\выключить тихие теги",
        "_cmd_doc_fuckall": "[чат] - Включить\\выключить авточтение",
        "_cmd_doc_fuckchats": "Показать активные авточтения в чатах",
        "_cls_doc": "Автоматически читает теги в выбранных чатах",
    }

    async def client_ready(self, client, db):
        self._db = db
        self._client = client
        self._ratelimit = []

    async def fucktagscmd(self, message: Message):
        """[chat] - Toggle notags"""
        args = utils.get_args_raw(message)
        try:
            try:
                args = int(args)
            except Exception:
                pass
            cid = (await self._client.get_entity(args)).id
        except Exception:
            cid = utils.get_chat_id(message)

        self._ratelimit = list(set(self._ratelimit) - set([cid]))

        if cid not in self.get("tags", []):
            self.set("tags", self.get("tags", []) + [cid])
            await utils.answer(message, self.strings("on"))
        else:
            self.set(
                "tags",
                list(set(self.get("tags", [])) - set([cid])),
            )
            await utils.answer(message, self.strings("off"))

    async def fuckallcmd(self, message: Message):
        """[chat] - Toggle autoread"""
        args = utils.get_args_raw(message)
        try:
            if str(args).isdigit():
                args = int(args)
            cid = (await self._client.get_entity(args)).id
        except Exception:
            cid = utils.get_chat_id(message)

        if cid not in self.get("strict", []):
            self.set("strict", self.get("strict", []) + [cid])
            await utils.answer(message, self.strings("on_strict"))
            return

        self.set(
            "strict",
            list(set(self.get("strict", [])) - set([cid])),
        )
        await utils.answer(message, self.strings("off_strict"))

    async def fuckchatscmd(self, message: Message):
        """Показать активные авточтения в чатах"""
        res = "<b>== FuckTags ==</b>\n"
        for chat in self.get("tags", []):
            try:
                c = await self._client.get_entity(chat)
                res += (c.title if c.title is not None else c.first_name) + "\n"
            except Exception:
                res += str(chat) + "\n"

        res += "\n<b>== FuckMessages ==</b>\n"
        for chat in self.get("strict", []):
            try:
                c = await self._client.get_entity(chat)
                res += (c.title if c.title is not None else c.first_name) + "\n"
            except Exception:
                res += str(chat) + "\n"

        await utils.answer(message, res)

    async def watcher(self, message: Message):
        if not hasattr(message, "text") or not isinstance(message, Message):
            return

        if utils.get_chat_id(message) in self.get("tags", []) and message.mentioned:
            await self._client.send_read_acknowledge(
                message.peer_id,
                message,
                clear_mentions=True,
            )

            if utils.get_chat_id(message) not in self._ratelimit:
                msg = await utils.answer(message, self.strings("do_not_tag_me"))
                self._ratelimit += [utils.get_chat_id(message)]
                await asyncio.sleep(2)
                await msg.delete()
        elif utils.get_chat_id(message) in self.get("strict", []):
            await self._client.send_read_acknowledge(message.peer_id, message)
