#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://static.hikari.gay/tagall_icon.png
# meta developer: @hikarimods
# meta banner: https://mods.hikariatama.ru/badges/tagall.jpg
# scope: hikka_min 1.3.0

import asyncio
import contextlib
import logging

from telethon.tl.types import Message
from telethon.tl.functions.channels import InviteToChannelRequest
from aiogram import Bot

from .. import loader, utils
from ..inline.types import InlineCall

logger = logging.getLogger(__name__)


class StopEvent:
    def __init__(self):
        self.state = True

    def stop(self):
        self.state = False


@loader.tds
class TagAllMod(loader.Module):
    """Tags all people in chat with either inline bot or client"""

    strings = {
        "name": "TagAll",
        "bot_error": "🚫 <b>Unable to invite inline bot to chat</b>",
        "_cfg_doc_default_message": "Default message of mentions",
        "_cfg_doc_delete": "Delete messages after tagging",
        "_cfg_doc_use_bot": "Use inline bot to tag people",
        "_cfg_doc_timeout": "What time interval to sleep between each tag message",
        "_cfg_doc_silent": "Do not send message with cancel button",
        "gathering": "🧚‍♀️ <b>Calling participants of this chat...</b>",
        "cancel": "🚫 Cancel",
        "cancelled": "🧚‍♀️ <b>TagAll cancelled!</b>",
    }

    strings_ru = {
        "bot_error": "🚫 <b>Не получилось пригласить бота в чат</b>",
        "_cls_doc": (
            "Отмечает всех участников чата, используя инлайн бот или классическим"
            " методом"
        ),
        "_cfg_doc_default_message": "Сообщение по умолчанию для тегов",
        "_cfg_doc_delete": "Удалять сообщения после тега",
        "_cfg_doc_use_bot": "Использовать бота для тегов",
        "_cfg_doc_timeout": "Время между сообщениями с тегами",
        "_cfg_doc_silent": "Не отправлять сообщение с кнопкой отмены",
        "gathering": "🧚‍♀️ <b>Отмечаю участников чата...</b>",
        "cancel": "🚫 Отмена",
        "cancelled": "🧚‍♀️ <b>Сбор участников отменен!</b>",
    }

    strings_de = {
        "bot_error": "🚫 <b>Einladung des Inline-Bots in den Chat fehlgeschlagen</b>",
        "_cfg_doc_default_message": "Standardnachricht für Erwähnungen",
        "_cfg_doc_delete": "Nachrichten nach Erwähnung löschen",
        "_cfg_doc_use_bot": "Inline-Bot verwenden, um Leute zu erwähnen",
        "_cfg_doc_timeout": (
            "Zeitintervall, in dem zwischen den Erwähnungen gewartet wird"
        ),
        "_cfg_doc_silent": "Nachricht ohne Abbrechen-Button senden",
        "gathering": "🧚‍♀️ <b>Erwähne Teilnehmer dieses Chats...</b>",
        "cancel": "🚫 Abbrechen",
        "cancelled": "🧚‍♀️ <b>TagAll abgebrochen!</b>",
    }

    strings_tr = {
        "bot_error": "🚫 <b>Inline botunu sohbete davet edilemedi</b>",
        "_cfg_doc_default_message": "Varsayılan etiket mesajı",
        "_cfg_doc_delete": "Etiketledikten sonra mesajları sil",
        "_cfg_doc_use_bot": "İnsanları etiketlemek için inline botu kullan",
        "_cfg_doc_timeout": "Her etiket mesajı arasında ne kadar bekleneceği",
        "_cfg_doc_silent": "İptal düğmesi olmadan mesaj gönderme",
        "gathering": "🧚‍♀️ <b>Bu sohbetteki katılımcıları çağırıyorum...</b>",
        "cancel": "🚫 İptal",
        "cancelled": "🧚‍♀️ <b>TagAll iptal edildi!</b>",
    }

    strings_hi = {
        "bot_error": "🚫 <b>इनलाइन बॉट को चैट में आमंत्रित करने में विफल रहा</b>",
        "_cfg_doc_default_message": "डिफ़ॉल्ट संदेश को उल्लेख करें",
        "_cfg_doc_delete": "टैग करने के बाद संदेश को हटाएं",
        "_cfg_doc_use_bot": "लोगों को टैग करने के लिए इनलाइन बॉट का उपयोग करें",
        "_cfg_doc_timeout": "प्रत्येक टैग संदेश के बीच कैसे स्लीप करना है",
        "_cfg_doc_silent": "रद्द बटन नहीं भेजने के लिए संदेश भेजें",
        "gathering": "🧚‍♀️ <b>इस चैट के भागीदारों को कॉल कर रहा हूं...</b>",
        "cancel": "🚫 रद्द करें",
        "cancelled": "🧚‍♀️ <b>TagAll रद्द कर दिया गया है!</b>",
    }

    strings_uz = {
        "bot_error": (
            "🚫 <b>Inline botni chatga taklif qilish muvaffaqiyatsiz bo‘ldi</b>"
        ),
        "_cfg_doc_default_message": "Odatiy etiket xabari",
        "_cfg_doc_delete": "Etiketdan so‘ng xabarlarni o‘chirish",
        "_cfg_doc_use_bot": "Odamlarni etiketlash uchun inline botdan foydalanish",
        "_cfg_doc_timeout": "Har bir etiket xabari orasida nechta kutish kerak",
        "_cfg_doc_silent": "Bekor tugmasi olmadan xabar jo‘natish",
        "gathering": "🧚‍♀️ <b>Ushbu chatta qatnashganlarni chaqiraman...</b>",
        "cancel": "🚫 Bekor qilish",
        "cancelled": "🧚‍♀️ <b>TagAll bekor qilindi!</b>",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "default_message",
                "@all",
                lambda: self.strings("_cfg_doc_default_message"),
            ),
            loader.ConfigValue(
                "delete",
                False,
                lambda: self.strings("_cfg_doc_delete"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "use_bot",
                False,
                lambda: self.strings("_cfg_doc_use_bot"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "timeout",
                0.1,
                lambda: self.strings("_cfg_doc_timeout"),
                validator=loader.validators.Float(minimum=0),
            ),
            loader.ConfigValue(
                "silent",
                False,
                lambda: self.strings("_cfg_doc_silent"),
                validator=loader.validators.Boolean(),
            ),
        )

    async def cancel(self, call: InlineCall, event: StopEvent):
        event.stop()
        await call.answer(self.strings("cancel"))

    @loader.command(
        groups=True,
        ru_doc="[текст] - Отметить всех участников чата",
        de_doc="[Text] - Alle Chatteilnehmer erwähnen",
        tr_doc="[metin] - Sohbet katılımcılarını etiketle",
        hi_doc="[पाठ] - चैट के सभी भागीदारों को टैग करें",
        uz_doc="[matn] - Chat qatnashuvchilarini tegish",
    )
    async def tagall(self, message: Message):
        """[text] - Tag all users in chat"""
        args = utils.get_args_raw(message)
        if message.out:
            await message.delete()

        if self.config["use_bot"]:
            try:
                await self._client(
                    InviteToChannelRequest(message.peer_id, [self.inline.bot_username])
                )
            except Exception:
                await utils.answer(message, self.strings("bot_error"))
                return

            with contextlib.suppress(Exception):
                Bot.set_instance(self.inline.bot)

            chat_id = int(f"-100{utils.get_chat_id(message)}")
        else:
            chat_id = utils.get_chat_id(message)

        event = StopEvent()

        if not self.config["silent"]:
            cancel = await self.inline.form(
                message=message,
                text=self.strings("gathering"),
                reply_markup={
                    "text": self.strings("cancel"),
                    "callback": self.cancel,
                    "args": (event,),
                },
            )

        for chunk in utils.chunks(
            [
                f'<a href="tg://user?id={user.id}">\xad</a>'
                async for user in self._client.iter_participants(message.peer_id)
            ],
            5,
        ):
            m = await (
                self.inline.bot.send_message
                if self.config["use_bot"]
                else self._client.send_message
            )(
                chat_id,
                utils.escape_html(args or self.config["default_message"])
                + "\xad".join(chunk),
            )

            if self.config["delete"]:
                with contextlib.suppress(Exception):
                    await m.delete()

            async def _task():
                nonlocal event, cancel
                if not self.config["silent"]:
                    return

                while True:
                    if not event.state:
                        await cancel.edit(self.strings("cancelled"))
                        return

                    await asyncio.sleep(0.1)

            task = asyncio.ensure_future(_task())
            await asyncio.sleep(self.config["timeout"])
            task.cancel()
            if not event.state:
                break

        await cancel.delete()
