#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://static.hikari.gay/dnd_statuses_icon.png
# meta banner: https://mods.hikariatama.ru/badges/dnd_statuses.jpg
# meta developer: @hikarimods
# scope: hikka_only
# scope: hikka_min 1.3.0

import asyncio
import logging

from telethon.tl.types import Message

from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class StatusesMod(loader.Module):
    """AFK Module analog with extended functionality"""

    strings = {
        "name": "Statuses",
        "status_not_found": "<b>🚫 Status not found</b>",
        "status_set": "<b>✅ Status set\n</b><code>{}</code>\nNotify: {}",
        "pzd_with_args": "<b>🚫 Args are incorrect</b>",
        "status_created": "<b>✅ Status {} created\n</b><code>{}</code>\nNotify: {}",
        "status_removed": "<b>✅ Status {} deleted</b>",
        "no_status": "<b>🚫 No status is active</b>",
        "status_unset": "<b>✅ Status removed</b>",
        "available_statuses": "<b>🦊 Available statuses:</b>\n\n",
    }

    strings_ru = {
        "status_not_found": "<b>🚫 Статус не найден</b>",
        "status_set": "<b>✅ Статус установлен\n</b><code>{}</code>\nУведомлять: {}",
        "pzd_with_args": "<b>🚫 Неверные аргументы</b>",
        "status_created": "<b>✅ Статус {} создан\n</b><code>{}</code>\nУведомлять: {}",
        "status_removed": "<b>✅ Статус {} удален</b>",
        "no_status": "<b>🚫 Сейчас нет активного статуса</b>",
        "status_unset": "<b>✅ Статус удален</b>",
        "available_statuses": "<b>🦊 Доступные статусы:</b>\n\n",
        "_cmd_doc_status": "<short_name> - Установить статус",
        "_cmd_doc_newstatus": (
            "<short_name> <уведомлять|0/1> <текст> - Создать новый статус\nПример:"
            " .newstatus test 1 Hello!"
        ),
        "_cmd_doc_delstatus": "<short_name> - Удалить статус",
        "_cmd_doc_unstatus": "Удалить статус",
        "_cmd_doc_statuses": "Показать доступные статусы",
        "_cls_doc": "AFK модуль с расширенным функционалом",
    }

    async def client_ready(self, *_):
        self._ratelimit = []
        self._sent_messages = []

    @loader.tag("only_messages", "in")
    async def watcher(self, message: Message):
        if not self.get("status", False):
            return

        if message.is_private:
            user = await message.get_sender()
            if user.id in self._ratelimit or user.is_self or user.bot or user.verified:
                return
        elif not message.mentioned:
            return

        chat = utils.get_chat_id(message)

        if chat in self._ratelimit:
            return

        m = await utils.answer(
            message,
            self.get("texts", {"": ""})[self.get("status", "")],
        )

        self._sent_messages += [m]

        if not self.get("notif", {"": False})[self.get("status", "")]:
            await self._client.send_read_acknowledge(
                message.peer_id,
                clear_mentions=True,
            )

        self._ratelimit += [chat]

    async def statuscmd(self, message: Message):
        """<short_name> - Set status"""
        args = utils.get_args_raw(message)
        if args not in self.get("texts", {}):
            await utils.answer(message, self.strings("status_not_found"))
            await asyncio.sleep(3)
            await message.delete()
            return

        self.set("status", args)
        self._ratelimit = []
        await utils.answer(
            message,
            self.strings("status_set").format(
                utils.escape_html(self.get("texts", {})[args]),
                str(self.get("notif")[args]),
            ),
        )

    async def newstatuscmd(self, message: Message):
        """<short_name> <notif|0/1> <text> - New status
        Example: .newstatus test 1 Hello!"""
        args = utils.get_args_raw(message)
        args = args.split(" ", 2)
        if len(args) < 3:
            await utils.answer(message, self.strings("pzd_with_args"))
            await asyncio.sleep(3)
            await message.delete()
            return

        args[1] = args[1] in ["1", "true", "yes", "+"]
        texts = self.get("texts", {})
        texts[args[0]] = args[2]
        self.set("texts", texts)

        notif = self.get("notif", {})
        notif[args[0]] = args[1]
        self.set("notif", notif)
        await utils.answer(
            message,
            self.strings("status_created").format(
                utils.escape_html(args[0]),
                utils.escape_html(args[2]),
                args[1],
            ),
        )

    async def delstatuscmd(self, message: Message):
        """<short_name> - Delete status"""
        args = utils.get_args_raw(message)
        if args not in self.get("texts", {}):
            await utils.answer(message, self.strings("status_not_found"))
            await asyncio.sleep(3)
            await message.delete()
            return

        texts = self.get("texts", {})
        del texts[args]
        self.set("texts", texts)

        notif = self.get("notif", {})
        del notif[args]
        self.set("notif", notif)
        await utils.answer(
            message,
            self.strings("status_removed").format(utils.escape_html(args)),
        )

    async def unstatuscmd(self, message: Message):
        """Remove status"""
        if not self.get("status", False):
            await utils.answer(message, self.strings("no_status"))
            await asyncio.sleep(3)
            await message.delete()
            return

        self.set("status", False)
        self._ratelimit = []

        for m in self._sent_messages:
            try:
                await m.delete()
            except Exception:
                logger.exception("Message not deleted due to")

        self._sent_messages = []

        await utils.answer(message, self.strings("status_unset"))

    async def statusescmd(self, message: Message):
        """Show available statuses"""
        res = self.strings("available_statuses")
        for short_name, status in self.get("texts", {}).items():
            res += (
                f"<b><u>{short_name}</u></b> | Notify:"
                f" <b>{self.get('notif', {})[short_name]}</b>\n{status}\n➖➖➖➖➖➖➖➖➖\n"
            )

        await utils.answer(message, res)
