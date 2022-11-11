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

    strings_de = {
        "status_not_found": "<b>🚫 Status nicht gefunden</b>",
        "status_set": "<b>✅ Status gesetzt\n</b><code>{}</code>\nBenachrichtigen: {}",
        "pzd_with_args": "<b>🚫 Falsche Argumente</b>",
        "status_created": (
            "<b>✅ Status {} erstellt\n</b><code>{}</code>\nBenachrichtigen: {}"
        ),
        "status_removed": "<b>✅ Status {} gelöscht</b>",
        "no_status": "<b>🚫 Es ist kein Status aktiv</b>",
        "status_unset": "<b>✅ Status gelöscht</b>",
        "available_statuses": "<b>🦊 Verfügbarer Status:</b>\n\n",
        "_cmd_doc_status": "<short_name> - Setze Status",
        "_cmd_doc_newstatus": (
            "<short_name> <benachrichtigen|0/1> <text> - Erstelle neuen"
            " Status\nBeispiel: .newstatus test 1 Hallo!"
        ),
        "_cmd_doc_delstatus": "<short_name> - Lösche Status",
        "_cmd_doc_unstatus": "Lösche Status",
        "_cmd_doc_statuses": "Zeige verfügbare Status",
        "_cls_doc": "AFK Modul mit erweitertem Funktionsumfang",
    }

    strings_uz = {
        "status_not_found": "<b>🚫 Status topilmadi</b>",
        "status_set": "<b>✅ Status o'rnatildi\n</b><code>{}</code>\nBildirish: {}",
        "pzd_with_args": "<b>🚫 Argumetlarni xato kiritdingiz</b>",
        "status_created": (
            "<b>✅ Status {} yaratildi\n</b><code>{}</code>\nBildirish: {}"
        ),
        "status_removed": "<b>✅ Status {} o'chirildi</b>",
        "no_status": "<b>🚫 Hozircha aktiv status yo'q</b>",
        "status_unset": "<b>✅ Status o'chirildi</b>",
        "available_statuses": "<b>🦊 Mavjud statuslar:</b>\n\n",
        "_cmd_doc_status": "<short_name> - Statusni o'rnatish",
        "_cmd_doc_newstatus": (
            "<short_name> <bildirish|0/1> <matn> - Yangi status yaratish\nMasalan:"
            " .newstatus test 1 Salom!"
        ),
        "_cmd_doc_delstatus": "<short_name> - Statusni o'chirish",
        "_cmd_doc_unstatus": "Statusni o'chirish",
        "_cmd_doc_statuses": "Mavjud statuslarni ko'rsatish",
        "_cls_doc": "AFK moduli kengaytirilgan funktsiyalari bilan",
    }

    strings_tr = {
        "status_not_found": "<b>🚫 Durum bulunamadı</b>",
        "status_set": "<b>✅ Durum ayarlandı\n</b><code>{}</code>\nBildirim: {}",
        "pzd_with_args": "<b>🚫 Yanlış argümanlar</b>",
        "status_created": (
            "<b>✅ Durum {} oluşturuldu\n</b><code>{}</code>\nBildirim: {}"
        ),
        "status_removed": "<b>✅ Durum {} kaldırıldı</b>",
        "no_status": "<b>🚫 Şu anda aktif durum yok</b>",
        "status_unset": "<b>✅ Durum kaldırıldı</b>",
        "available_statuses": "<b>🦊 Mevcut durumlar:</b>\n\n",
        "_cmd_doc_status": "<short_name> - Durum ayarla",
        "_cmd_doc_newstatus": (
            "<short_name> <bildirim|0/1> <metin> - Yeni durum oluştur\nÖrnek:"
            " .newstatus test 1 Merhaba!"
        ),
        "_cmd_doc_delstatus": "<short_name> - Durum kaldır",
        "_cmd_doc_unstatus": "Durum kaldır",
        "_cmd_doc_statuses": "Mevcut durumları göster",
        "_cls_doc": "AFK modülü genişletilmiş özelliklerle",
    }

    strings_hi = {
        "status_not_found": "<b>🚫 स्थिति नहीं मिली</b>",
        "status_set": "<b>✅ स्थिति सेट की गई\n</b><code>{}</code>\nसूचित करना: {}",
        "pzd_with_args": "<b>🚫 गलत तर्क</b>",
        "status_created": (
            "<b>✅ स्थिति {} बनाया गया\n</b><code>{}</code>\nसूचित करना: {}"
        ),
        "status_removed": "<b>✅ स्थिति {} हटाया गया</b>",
        "no_status": "<b>🚫 अभी कोई सक्रिय स्थिति नहीं है</b>",
        "status_unset": "<b>✅ स्थिति हटाया गया</b>",
        "available_statuses": "<b>🦊 उपलब्ध स्थितियां:</b>\n\n",
        "_cmd_doc_status": "<short_name> - स्थिति सेट करें",
        "_cmd_doc_newstatus": (
            "<short_name> <सूचित करना|0/1> <पाठ> - नया स्थिति बनाएं\nउदाहरण:"
            " .newstatus test 1 हैलो!"
        ),
        "_cmd_doc_delstatus": "<short_name> - स्थिति हटाएं",
        "_cmd_doc_unstatus": "स्थिति हटाएं",
        "_cmd_doc_statuses": "उपलब्ध स्थितियों को दिखाएं",
        "_cls_doc": "एफके मॉड्यूल विस्तारित सुविधाओं के साथ",
    }

    def __init__(self):
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
