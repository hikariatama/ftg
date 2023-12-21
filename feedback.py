#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://static.dan.tatar/feedback_icon.png
# meta banner: https://mods.hikariatama.ru/badges/feedback.jpg
# meta developer: @hikarimods
# scope: inline
# scope: hikka_only
# scope: hikka_min 1.2.10

import abc
import time

from aiogram.types import Message as AiogramMessage
from telethon.utils import get_display_name

from .. import loader, utils
from ..inline.types import InlineCall


@loader.tds
class FeedbackMod(loader.Module):
    """Simple feedback bot for Hikka"""

    __metaclass__ = abc.ABCMeta

    strings = {
        "name": "Feedback",
        "/start": (
            "🤵‍♀️ <b>Hello. I'm feedback bot of {}. Read /nometa before"
            " continuing</b>\n<b>You can send only one message per minute</b>"
        ),
        "/nometa": (
            "👨‍🎓 <b><u>Internet-talk rules:</u></b>\n\n"
            "<b>🚫 Do <u>not</u> send just 'Hello'</b>\n"
            "<b>🚫 Do <u>not</u> advertise</b>\n"
            "<b>🚫 Do <u>not</u> insult</b>\n"
            "<b>🚫 Do <u>not</u> split message</b>\n"
            "<b>✅ Write your question in one message</b>"
        ),
        "enter_message": "✍️ <b>Enter your message here</b>",
        "sent": "✅ <b>Your message has been sent to owner</b>",
    }

    strings_ru = {
        "/start": (
            "🤵‍♀️ <b>Привет. Я бот обратной связи {}. Прочитай /nometa перед"
            " продолжением</b>\n<b>Ты можешь отправлять только одно сообщение в"
            " минуту</b>"
        ),
        "enter_message": "✍️ <b>Ввведи сообщение</b>",
        "sent": "✅ <b>Сообщение передано владельцу</b>",
        "_cls_doc": "Бот обратной связи для Hikka",
        "/nometa": (
            "👨‍🎓 <b><u>Правила общения в Интернете:</u></b>\n\n <b>🚫 <u>Не пиши</u>"
            " просто 'Привет'</b>\n <b>🚫 <u>Не рекламируй </u> ничего</b>\n <b>🚫 <u>Не"
            " оскорбляй</u> никого</b>\n <b>🚫 <u>Не разбивай</u> сообщения на миллион"
            " кусочков</b>\n <b>✅ Пиши вопрос в одном сообщении</b>"
        ),
    }

    strings_de = {
        "/start": (
            "🤵‍♀️ <b>Hallo. Ich bin der Feedback-Bot von {}. Lies /nometa, bevor"
            " du fortfährst</b>\n<b>Du kannst nur eine Nachricht pro Minute senden</b>"
        ),
        "enter_message": "✍️ <b>Gib deine Nachricht hier ein</b>",
        "sent": "✅ <b>Deine Nachricht wurde dem Besitzer gesendet</b>",
        "_cls_doc": "Feedback-Bot für Hikka",
        "/nometa": (
            "👨‍🎓 <b><u>Internet-Talk-Regeln:</u></b>\n\n <b>🚫 <u>Nicht</u> 'Hallo'"
            " schreiben</b>\n <b>🚫 <u>Nicht</u> werben</b>\n <b>🚫 <u>Nicht</u>"
            " beleidigen</b>\n <b>🚫 <u>Nicht</u> aufteilen</b>\n <b>✅ Schreibe deine"
            " Frage in einer Nachricht</b>"
        ),
    }

    strings_hi = {
        "/start": (
            "🤵‍♀️ <b>नमस्ते। मैं {} का फीडबैक बॉट हूँ। जारी रखने से पहले /nometa"
            " पढ़ें</b>\n<b>आप मिनट में केवल एक संदेश भेज सकते हैं</b>"
        ),
        "enter_message": "✍️ <b>यहां संदेश दर्ज करें</b>",
        "sent": "✅ <b>आपका संदेश मालिक को भेज दिया गया है</b>",
        "_cls_doc": "Hikka के लिए प्रतिक्रिया बॉट",
        "/nometa": (
            "👨‍🎓 <b><u>इंटरनेट बातचीत नियम:</u></b>\n\n <b>🚫 'नमस्ते' न लिखें</b>\n"
            " <b>🚫 विज्ञापन न करें</b>\n <b>🚫 अपमान न करें</b>\n <b>🚫 संदेश को विभाजित"
            " न करें</b>\n <b>✅ अपना सवाल एक संदेश में लिखें</b>"
        ),
    }

    strings_tr = {
        "/start": (
            "🤵‍♀️ <b>Merhaba. Ben {}'ın geri bildirim botuyum. Devam etmeden önce"
            " /nometa'ya bakın</b>\n<b>Sadece bir dakikada bir mesaj"
            " gönderebilirsiniz</b>"
        ),
        "enter_message": "✍️ <b>Mesajınızı buraya girin</b>",
        "sent": "✅ <b>Sahibine mesajınız gönderildi</b>",
        "_cls_doc": "Hikka için geri bildirim botu",
        "/nometa": (
            "👨‍🎓 <b><u>İnternet Konuşma Kuralları:</u></b>\n\n <b>🚫 'Merhaba'"
            " yazmayın</b>\n <b>🚫 Reklam yapmayın</b>\n <b>🚫 Kimsenin ağzına"
            " sıçramayın</b>\n <b>🚫 Mesajı parçalaymayın</b>\n <b>✅ Sorunuzu bir"
            " mesajda yazın</b>"
        ),
    }

    async def client_ready(self):
        self._name = utils.escape_html(get_display_name(self._client.hikka_me))
        self._ratelimit = {}
        self._markup = self.inline.generate_markup(
            {"text": "✍️ Leave a message [1 per minute]", "data": "fb_leave_message"}
        )
        self._cancel = self.inline.generate_markup(
            {"text": "🚫 Cancel", "data": "fb_cancel"}
        )

        self.__doc__ = (
            "Feedback bot\n"
            f"Your feeback link: t.me/{self.inline.bot_username}?start=feedback\n"
            "You can freely share it"
        )

    async def aiogram_watcher(self, message: AiogramMessage):
        if message.text == "/start feedback":
            await message.answer(
                self.strings("/start").format(self._name),
                reply_markup=self._markup,
            )
        elif message.text == "/nometa":
            await message.answer(self.strings("/nometa"), reply_markup=self._markup)
        elif self.inline.gs(message.from_user.id) == "fb_send_message":
            await self.inline.bot.forward_message(
                self._tg_id,
                message.chat.id,
                message.message_id,
            )
            await message.answer(self.strings("sent"))
            self._ratelimit[message.from_user.id] = time.time() + 60
            self.inline.ss(message.from_user.id, False)

    @loader.inline_everyone
    @loader.callback_handler()
    async def feedback(self, call: InlineCall):
        """Handles button clicks"""
        if call.data == "fb_cancel":
            self.inline.ss(call.from_user.id, False)
            await self.inline.bot.delete_message(
                call.message.chat.id,
                call.message.message_id,
            )
            return

        if call.data != "fb_leave_message":
            return

        if (
            call.from_user.id in self._ratelimit
            and self._ratelimit[call.from_user.id] > time.time()
        ):
            await call.answer(
                (
                    "You can send next message in"
                    f" {self._ratelimit[call.from_user.id] - time.time():.0f} second(-s)"
                ),
                show_alert=True,
            )
            return

        self.inline.ss(call.from_user.id, "fb_send_message")
        await self.inline.bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=self.strings("enter_message"),
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_markup=self._cancel,
        )
