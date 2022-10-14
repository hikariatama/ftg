__version__ = (3, 0, 4)

#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta title: PM->BL
# meta pic: https://img.icons8.com/external-dreamcreateicons-flat-dreamcreateicons/512/000000/external-death-halloween-dreamcreateicons-flat-dreamcreateicons.png
# meta banner: https://mods.hikariatama.ru/badges/pmbl.jpg
# meta developer: @hikarimods
# scope: hikka_only
# scope: hikka_min 1.5.0

import logging
import time
import contextlib
from typing import Optional

from telethon.tl.functions.contacts import BlockRequest
from telethon.tl.functions.messages import DeleteHistoryRequest, ReportSpamRequest
from telethon.tl.types import Message, PeerUser, User
from telethon.utils import get_display_name, get_peer_id

from .. import loader, utils

logger = logging.getLogger(__name__)


def format_(state: Optional[bool]) -> str:
    if state is None:
        return "❔"

    return "🫡" if state else "🙅‍♂️ Not"


@loader.tds
class PMBLMod(loader.Module):
    """Bans and reports incoming messages from unknown users"""

    strings = {
        "name": "PMBL",
        "state": (
            "<emoji document_id=5314803591058301611>🛡</emoji> <b>PM->BL is now"
            " {}</b>\n<i>Report spam? - {}\nDelete dialog? - {}</i>"
        ),
        "args": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Usage example:"
            " </b><code>.pmblsett 0 0</code>"
        ),
        "args_pmban": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Usage example:"
            " </b><code>.pmbanlast 5</code>"
        ),
        "banned": (
            "<emoji document_id=5375414397172717975>😃</emoji> <b>Hey there"
            " •ᴗ•</b>\n<b>Unit «SIGMA»<b>, the <b>guardian</b> of this account. You are"
            " <b>not approved</b>! You can contact my owner <b>in chat</b>, if you need"
            " help.\n<b>I need to ban you in terms of security</b>"
        ),
        "removing": (
            "<emoji document_id=5456529570431770384>🚮</emoji> <b>Removing {} last"
            " dialogs...</b>"
        ),
        "removed": (
            "<emoji document_id=5456529570431770384>🚮</emoji> <b>Removed {} last"
            " dialogs!</b>"
        ),
        "user_not_specified": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>You haven't specified"
            " user</b>"
        ),
        "approved": (
            "<emoji document_id=5461129450341014019>✋</emoji> <b><a"
            ' href="tg://user?id={}">{}</a> approved in pm</b>'
        ),
        "banned_log": (
            '👮 <b>I banned <a href="tg://user?id={}">{}</a>.</b>\n\n<b>{} Reported'
            " spam</b>\n<b>{} Deleted dialog</b>\n\n<b><emoji"
            " document_id=5312526098750252863>🚫</emoji> Message</b>\n<code>{}</code>"
        ),
        "hello": (
            "🔏 <b>Unit «SIGMA»</b> protects your personal messages from intrusions. It"
            " will block everyone, who's trying to invade you.\n\nUse"
            " <code>.pmbl</code> to enable protection, <code>.pmblsett</code> to"
            " configure it and <code>.pmbanlast</code> if you've already been"
            " pm-raided."
        ),
    }

    strings_ru = {
        "state": (
            "<emoji document_id=5314803591058301611>🛡</emoji> <b>Текущее состояние"
            " PM->BL: {}</b>\n<i>Сообщать о спаме? - {}\nУдалять диалог? - {}</i>"
        ),
        "args": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Пример:"
            " </b><code>.pmblsett 0 0</code>"
        ),
        "args_pmban": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Пример:"
            " </b><code>.pmbanlast 5</code>"
        ),
        "banned": (
            "<emoji document_id=5375414397172717975>😃</emoji> <b>Добрый день"
            " •ᴗ•</b>\n<b>Юнит «SIGMA»<b>, <b>защитник</b> этого аккаунта. Вы <b>не"
            " потверждены</b>! Вы можете связаться с моим владельцем <b>в чате</b>,"
            " если нужна помощь.\n<b>Я вынужден заблокировать вас из соображений"
            " безопасности</b>"
        ),
        "hello": (
            "🔏 <b>Юнит «SIGMA»</b> защищает твои личные сообщенния от неизвестных"
            " пользователей. Он будет блокировать всех, кто не соответствует"
            " настройкам.\n\nВведи <code>.pmbl</code> для активации защиты,"
            " <code>.pmblsett</code> для ее настройки и <code>.pmbanlast</code> если"
            " нужно очистить уже прошедший рейд на личные сообщения."
        ),
        "removing": (
            "<emoji document_id=5456529570431770384>🚮</emoji> <b>Удаляю {} последних"
            " диалогов...</b>"
        ),
        "removed": (
            "<emoji document_id=5456529570431770384>🚮</emoji> <b>Удалил {} последних"
            " диалогов!</b>"
        ),
        "user_not_specified": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Укажи пользователя</b>"
        ),
        "_cmd_doc_pmbl": "Включить или выключить защиту",
        "_cmd_doc_pmbanlast": (
            "<количество> - Забанить и удалить n последних диалогов с пользователями"
        ),
        "_cmd_doc_allowpm": "<пользователь> - Разрешить пользователю писать тебе в ЛС",
        "_cls_doc": "Блокирует и репортит входящие сообщения от незнакомцев",
        "approved": (
            "<emoji document_id=5461129450341014019>✋</emoji> <b><a"
            ' href="tg://user?id={}">{}</a> одобрен в лс</b>'
        ),
        "banned_log": (
            '👮 <b>Я заблокировал <a href="tg://user?id={}">{}</a>.</b>\n\n<b>{} Сообщил'
            " о спаме</b>\n<b>{} Удалил диалог</b>\n\n<b><emoji"
            " document_id=5312526098750252863>🚫</emoji> Сообщение</b>\n<code>{}</code>"
        ),
    }

    strings_de = {
        "state": (
            "<emoji document_id=5314803591058301611>🛡</emoji> <b>Aktueller PM->BL"
            " Status: {}</b>\n<i>Spam melden? - {}\nDialoge löschen? - {}</i>"
        ),
        "args": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Beispiel:"
            " </b><code>.pmblsett 0 0</code>"
        ),
        "args_pmban": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Beispiel:"
            " </b><code>.pmbanlast 5</code>"
        ),
        "banned": (
            "<emoji document_id=5375414397172717975>😃</emoji> <b>Hallo"
            " •ᴗ•</b>\n<b>Einheit «SIGMA»<b>, <b>der Schutz dieses Accounts</b>. Sie"
            " sind <b>nicht autorisiert</b>! Sie können sich an den Besitzer meines"
            " Accounts wenden, wenn Sie Hilfe benötigen.\n<b>Ich bin gezwungen, Sie aus"
            " Sicherheitsgründen zu sperren</b>"
        ),
        "hello": (
            "🔏 <b>Einheit «SIGMA»</b> schützt Ihre persönlichen Nachrichten vor"
            " unbekannten Benutzern. Es wird alle blockieren, die nicht den"
            " Einstellungen entsprechen.\n\nGeben Sie <code>.pmbl</code> ein, um die"
            " Schutzfunktion zu aktivieren, <code>.pmblsett</code> zum Konfigurieren"
            " und <code>.pmbanlast</code>, wenn Sie bereits einen Raid auf Ihre"
            " persönlichen Nachrichten durchgeführt haben."
        ),
        "removing": (
            "<emoji document_id=5456529570431770384>🚮</emoji> <b>Entferne {} letzte"
            " Dialoge...</b>"
        ),
        "removed": (
            "<emoji document_id=5456529570431770384>🚮</emoji> <b>Entfernt {} letzte"
            " Dialoge!</b>"
        ),
        "user_not_specified": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Du hast keinen"
            " Benutzer angegeben</b>"
        ),
        "_cmd_doc_pmbl": "Aktiviert oder deaktiviert den Schutz",
        "_cmd_doc_pmbanlast": (
            "<Anzahl> - Bannt und löscht n letzte Dialoge mit Benutzern"
        ),
        "_cmd_doc_allowpm": (
            "<Benutzer> - Erlaubt dem Benutzer, dir eine private Nachricht zu senden"
        ),
        "_cls_doc": "Blockiert und meldet eingehende Nachrichten von Unbekannten",
        "approved": (
            "<emoji document_id=5461129450341014019>✋</emoji> <b><a"
            ' href="tg://user?id={}">{}</a> wurde in den Ls genehmigt</b>'
        ),
        "banned_log": (
            '👮 <b>Ich habe <a href="tg://user?id={}">{}</a> geblockt.</b>\n\n<b>{} Hat'
            " über Spam berichtet</b>\n<b>{} Hat den Dialog gelöscht</b>\n\n<b><emoji"
            " document_id=5312526098750252863>🚫</emoji> Nachricht</b>\n<code>{}</code>"
        ),
    }

    strings_tr = {
        "state": (
            "<emoji document_id=5314803591058301611>🛡</emoji> <b>Şu anki PM->BL durumu:"
            " {}</b>\n<i>Spam rapor edilsin mi? - {}\nSohbetler silinsin mi? - {}</i>"
        ),
        "args": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Örnek:"
            " </b><code>.pmblsett 0 0</code>"
        ),
        "args_pmban": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Örnek:"
            " </b><code>.pmbanlast 5</code>"
        ),
        "banned": (
            "<emoji document_id=5375414397172717975>😃</emoji> <b>Merhaba"
            " •ᴗ•</b>\n<b>«SIGMA» birimi</b>, <b>hesabınızın koruması</b>. <b>Yetkili"
            " değilsiniz</b>! Yardım için hesabımın sahibi ile iletişime"
            " geçebilirsiniz.\n<b>Güvenlik nedeniyle sizi zorunlu olarak"
            " engelliyorum</b>"
        ),
        "hello": (
            "🔏 <b>«SIGMA» birimi</b>, tanımadığınız kullanıcılarla kişisel"
            " mesajlarınızı korur. Ayarlara uygun olmayanları tümünü engeller.\n\n"
            "<code>.pmbl</code> yazarak koruma özelliğini etkinleştirebilir, "
            "<code>.pmblsett</code> yazarak yapılandırabilir ve zaten kişisel"
            " mesajlarınıza bir raid gerçekleştirdiyseniz <code>.pmbanlast</code>"
            " yazarak bunu gerçekleştirebilirsiniz."
        ),
        "removing": (
            "<emoji document_id=5456529570431770384>🚮</emoji> <b>Son {} sohbet"
            " siliniyor...</b>"
        ),
        "removed": (
            "<emoji document_id=5456529570431770384>🚮</emoji> <b>Son {} sohbet"
            " silindi!</b>"
        ),
        "user_not_specified": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Bir kullanıcı"
            " belirtmediniz</b>"
        ),
        "_cmd_doc_pmbl": "Korumayı etkinleştirir veya devre dışı bırakır",
        "_cmd_doc_pmbanlast": "<sayı> - Kullanıcılarla son n sohbeti yasaklar ve siler",
        "_cmd_doc_allowpm": (
            "<kullanıcı> - Kullanıcıya kişisel mesaj göndermeye izin verir"
        ),
        "_cls_doc": (
            "Tanımadığınız kullanıcıların gelen mesajlarını engeller ve rapor eder"
        ),
        "approved": (
            "<emoji document_id=5461129450341014019>✋</emoji> <b><a"
            ' href="tg://user?id={}">{}</a> Ls listesine eklendi</b>'
        ),
        "banned_log": (
            '👮 <b><a href="tg://user?id={}">{}</a> engellendi.</b>\n\n<b>{} Spam rapor'
            " etti</b>\n<b>{} Sohbeti sildi</b>\n\n<b><emoji"
            " document_id=5312526098750252863>🚫</emoji> Mesaj</b>\n<code>{}</code>"
        ),
    }

    strings_uz = {
        "state": (
            "<emoji document_id=5314803591058301611>🛡</emoji> <b>Joriy PM->BL holati:"
            " {}</b>\n<i>Spam haqida xabar berilsinmi? - {}\nSuhbatlar o'chirilsinmi? -"
            " {}</i>"
        ),
        "args": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Misol:"
            " </b><code>.pmblsett 0 0</code>"
        ),
        "args_pmban": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Misol:"
            " </b><code>.pmbanlast 5</code>"
        ),
        "banned": (
            "<emoji document_id=5375414397172717975>😃</emoji> <b>Salom"
            " •ᴗ•</b>\n<b>«SIGMA» birimi</b>, <b>hisobingizni himoya</b>. <b>Ruxsat"
            " berilmaganingiz</b>! Yordam kerak bo'lsa hisobimning egasi bilan"
            " bog'lanishingiz mumkin.\n<b>Xavfsizlik sababli sizni majbur qilishim"
            " kerak</b>"
        ),
        "hello": (
            "🔏 <b>«SIGMA» birimi</b>, tanimaydigan foydalanuvchilar bilan"
            " shaxsiy xabarlarini himoya qiladi. Sozlamalarga mos bo'lmasa"
            " barchasini bloklashadi.\n\n<code>.pmbl</code> yozib himoya"
            " imkoniyatini yoqish, <code>.pmblsett</code> yozib konfiguratsiyani"
            " o'zgartirish va agar sizda shaxsiy xabarlariga raid bormi bo'lsa"
            " <code>.pmbanlast</code> yozib uni bajarishingiz mumkin."
        ),
        "removing": (
            "<emoji document_id=5456529570431770384>🚮</emoji> <b>Son {} suhbat"
            " o'chirilmoqda...</b>"
        ),
        "removed": (
            "<emoji document_id=5456529570431770384>🚮</emoji> <b>Son {} suhbat"
            " o'chirildi!</b>"
        ),
        "user_not_specified": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Siz foydalanuvchi"
            " belgilamadingiz</b>"
        ),
        "_cmd_doc_pmbl": "Himoyani yoqadi yoki o'chiradi",
        "_cmd_doc_pmbanlast": (
            "<son> - Foydalanuvchilar bilan son n suhbatni yasaklaydi"
        ),
        "_cmd_doc_allowpm": (
            "<foydalanuvchi> - Foydalanuvchiga shaxsiy xabar yuborishga ruxsat beradi"
        ),
        "_cls_doc": "Tanimaydigan foydalanuvchilar gelen xabarlarini bloklashadi",
        "approved": (
            "<emoji document_id=5461129450341014019>✋</emoji> <b><a"
            " href=\"tg://user?id={}\">{}</a> Ls ro'yxatiga qo'shildi</b>"
        ),
        "banned_log": (
            '👮 <b><a href="tg://user?id={}">{}</a> bloklandi.</b>\n\n<b>{} Spam xabar'
            " berdi</b>\n<b>{} Suhbat o'chirildi</b>\n\n<b><emoji"
            " document_id=5312526098750252863>🚫</emoji> Xabar</b>\n<code>{}</code>"
        ),
    }

    strings_hi = {
        "state": (
            "<emoji document_id=5314803591058301611>🛡</emoji> <b>वर्तमान PM->BL स्थिति:"
            " {}</b>\n<i>स्पैम रिपोर्ट करें? - {}\nडायलॉगहटाएं? - {}</i>"
        ),
        "args": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>उदाहरण:"
            " </b><code>.pmblsett 0 0</code>"
        ),
        "args_pmban": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>उदाहरण:"
            " </b><code>.pmbanlast 5</code>"
        ),
        "banned": (
            "<emoji document_id=5375414397172717975>😃</emoji> <b>नमस्ते"
            " •ᴗ•</b>\n<b>यूनिट «SIGMA»<b>, <b>इस खाते की सुरक्षा</b>. आप"
            " <b>अनधिकृत</b> हैं! आप मेरे खाते के मालिक को अपनी मदद के लिए या आपको"
            " सहायता की आवश्यकता है तो उसे संपर्क कर सकते हैं।\n<b>मैं आपको सुरक्षा के"
            " कारण बंद करने के लिए बाधित कर दूंगा</b>"
        ),
        "hello": (
            "🔏 <b>यूनिट «SIGMA»</b> अपने निजी संदेशों को अज्ञात उपयोगकर्ताओं से"
            " सुरक्षित करता है। इसे सेटिंग्स के अनुसार सभी ब्लॉक करेगा।\n\n<code>"
            ".pmbl</code> दर्ज करें, ताकि सुरक्षा कार्यक्षमता सक्रिय हो, <code>"
            ".pmblsett</code> कॉन्फ़िगर करने के लिए और <code>.pmbanlast</code>, जब आपने"
            " अपने निजी संदेशों पर एक रैड किया है।"
        ),
        "removing": (
            "<emoji document_id=5456529570431770384>🚮</emoji> <b>{} अंतिम डायलॉग हटा"
            " रहा है...</b>"
        ),
        "removed": (
            "<emoji document_id=5456529570431770384>🚮</emoji> <b>{} अंतिम डायलॉग हटा"
            " दिया!</b>"
        ),
        "user_not_specified": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>आपने किसी उपयोगकर्ता"
            " को नहीं निर्दिष्ट किया</b>"
        ),
        "_cmd_doc_pmbl": "सुरक्षा को सक्षम या अक्षम करता है",
        "_cmd_doc_pmbanlast": (
            "<अंक> - उपयोगकर्ताओं के साथ निजी संदेशों को ब्लॉक और हटाता है"
        ),
        "_cmd_doc_allowpm": (
            "<उपयोगकर्ता> - उपयोगकर्ता को आपको एक निजी संदेश भेजने की अनुमति देता है"
        ),
        "_cmd_doc_pmblsett": (
            "<ब्लॉक> <अनुमति> - ब्लॉक और अनुमति को सेट करता है, जब आपके पास एक निजी"
            " संदेश आता है"
        ),
        "_cls_doc": "एक निजी संदेश भेजने की अनुमति देता है",
    }

    def __init__(self):
        self._queue = []
        self._ban_queue = []
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "ignore_contacts",
                True,
                lambda: "Ignore contacts?",
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "ignore_active",
                True,
                lambda: "Ignore peers, where you participated?",
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "active_threshold",
                5,
                lambda: "What number of your messages is required to trust peer",
                validator=loader.validators.Integer(minimum=1),
            ),
            loader.ConfigValue(
                "custom_message",
                doc=lambda: "Custom message to notify untrusted peers. Leave empty for default one",
            ),
            loader.ConfigValue(
                "photo",
                "https://github.com/hikariatama/assets/raw/master/unit_sigma.png",
                lambda: "Photo, which is sent along with banned notification",
                validator=loader.validators.Link(),
            ),
            loader.ConfigValue(
                "report_spam",
                False,
                lambda: "Report spam?",
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "delete_dialog",
                False,
                lambda: "Delete dialog?",
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "silent",
                False,
                lambda: "Do not send anything to banned user",
                validator=loader.validators.Boolean(),
            ),
        )

    async def client_ready(self):
        self._whitelist = self.get("whitelist", [])
        self._ratelimit = []
        self._ratelimit_timeout = 5 * 60
        self._ratelimit_threshold = 10
        if not self.get("ignore_hello", False):
            await self.inline.bot.send_photo(
                self._tg_id,
                photo=(
                    r"https://github.com/hikariatama/assets/raw/master/unit_sigma.png"
                ),
                caption=self.strings("hello"),
                parse_mode="HTML",
            )

            self.set("ignore_hello", True)

    async def pmblcmd(self, message: Message):
        """Toggle PMBL"""
        current = self.get("state", False)
        new = not current
        self.set("state", new)
        await utils.answer(
            message,
            self.strings("state").format(
                "on" if new else "off",
                "yes" if self.config["report_spam"] else "no",
                "yes" if self.config["delete_dialog"] else "no",
            ),
        )

    async def pmbanlastcmd(self, message: Message):
        """<number> - Ban and delete dialogs with n most new users"""
        n = utils.get_args_raw(message)
        if not n or not n.isdigit():
            await utils.answer(message, self.strings("args_pmban"))
            return

        n = int(n)

        await utils.answer(message, self.strings("removing").format(n))

        dialogs = []
        async for dialog in self._client.iter_dialogs(ignore_pinned=True):
            try:
                if not isinstance(dialog.message.peer_id, PeerUser):
                    continue
            except AttributeError:
                continue

            m = (
                await self._client.get_messages(
                    dialog.message.peer_id,
                    limit=1,
                    reverse=True,
                )
            )[0]

            dialogs += [
                (
                    get_peer_id(dialog.message.peer_id),
                    int(time.mktime(m.date.timetuple())),
                )
            ]

        dialogs.sort(key=lambda x: x[1])
        to_ban = [d for d, _ in dialogs[::-1][:n]]

        for d in to_ban:
            await self._client(BlockRequest(id=d))

            await self._client(DeleteHistoryRequest(peer=d, just_clear=True, max_id=0))

        await utils.answer(message, self.strings("removed").format(n))

    def _approve(self, user: int, reason: str = "unknown"):
        self._whitelist += [user]
        self._whitelist = list(set(self._whitelist))
        self.set("whitelist", self._whitelist)
        logger.debug(f"User approved in pm {user}, filter: {reason}")
        return

    async def allowpmcmd(self, message: Message):
        """<reply or user> - Allow user to pm you"""
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()

        user = None

        try:
            user = await self._client.get_entity(args)
        except Exception:
            with contextlib.suppress(Exception):
                user = await self._client.get_entity(reply.sender_id) if reply else None

        if not user:
            chat = await message.get_chat()
            if not isinstance(chat, User):
                await utils.answer(message, self.strings("user_not_specified"))
                return

            user = chat

        self._approve(user.id, "manual_approve")
        await utils.answer(
            message, self.strings("approved").format(user.id, get_display_name(user))
        )

    async def watcher(self, message: Message):
        if (
            getattr(message, "out", False)
            or not isinstance(message, Message)
            or not isinstance(message.peer_id, PeerUser)
            or not self.get("state", False)
            or utils.get_chat_id(message)
            in {
                1271266957,  # @replies
                777000,  # Telegram Notifications
                self._tg_id,  # Self
            }
        ):
            return

        self._queue += [message]

    @loader.loop(interval=0.05, autostart=True)
    async def ban_loop(self):
        if not self._ban_queue:
            return

        message = self._ban_queue.pop(0)
        self._ratelimit = list(
            filter(
                lambda x: x + self._ratelimit_timeout < time.time(),
                self._ratelimit,
            )
        )

        dialog = None

        if len(self._ratelimit) < self._ratelimit_threshold:
            if not self.config["silent"]:
                try:
                    await self._client.send_file(
                        message.peer_id,
                        self.config["photo"],
                        caption=self.config["custom_message"] or self.strings("banned"),
                    )
                except Exception:
                    await utils.answer(
                        message,
                        self.config["custom_message"] or self.strings("banned"),
                    )

                self._ratelimit += [round(time.time())]

            try:
                dialog = await self._client.get_entity(message.peer_id)
            except ValueError:
                pass

        await self.inline.bot.send_message(
            self._client.tg_id,
            self.strings("banned_log").format(
                dialog.id if dialog is not None else message.sender_id,
                (
                    utils.escape_html(dialog.first_name)
                    if dialog is not None
                    else (
                        getattr(getattr(message, "sender", None), "username", None)
                        or message.sender_id
                    )
                ),
                format_(self.config["report_spam"]),
                format_(self.config["delete_dialog"]),
                utils.escape_html(
                    "<sticker"
                    if message.sticker
                    else "<photo>"
                    if message.photo
                    else "<video>"
                    if message.video
                    else "<file>"
                    if message.document
                    else message.raw_text[:3000]
                ),
            ),
            parse_mode="HTML",
            disable_web_page_preview=True,
        )

        await self._client(BlockRequest(id=message.sender_id))

        if self.config["report_spam"]:
            await self._client(ReportSpamRequest(peer=message.sender_id))

        if self.config["delete_dialog"]:
            await self._client(
                DeleteHistoryRequest(peer=message.sender_id, just_clear=True, max_id=0)
            )

        self._approve(message.sender_id, "banned")

        logger.warning(f"Intruder punished: {message.sender_id}")

    @loader.loop(interval=0.01, autostart=True)
    async def queue_processor(self):
        if not self._queue:
            return

        message = self._queue.pop(0)

        cid = utils.get_chat_id(message)
        if cid in self._whitelist:
            return

        peer = (
            getattr(getattr(message, "sender", None), "username", None)
            or message.peer_id
        )

        with contextlib.suppress(ValueError):
            entity = await self._client.get_entity(peer)

            if entity.bot:
                return self._approve(cid, "bot")

            if self.config["ignore_contacts"]:
                if entity.contact:
                    return self._approve(cid, "ignore_contacts")

        first_message = (
            await self._client.get_messages(
                peer,
                limit=1,
                reverse=True,
            )
        )[0]

        if (
            getattr(message, "raw_text", False)
            and first_message.sender_id == self._tg_id
        ):
            return self._approve(cid, "started_by_you")

        if self.config["ignore_active"]:
            q = 0

            async for msg in self._client.iter_messages(peer, limit=200):
                if msg.sender_id == self._tg_id:
                    q += 1

                if q >= self.config["active_threshold"]:
                    return self._approve(cid, "active_threshold")

        self._ban_queue += [message]

    @loader.debug_method(name="unwhitelist")
    async def denypm(self, message: Message):
        user = (await message.get_reply_message()).sender_id
        self.set("whitelist", list(set(self.get("whitelist", [])) - {user}))
        return f"User unwhitelisted: {user}"
