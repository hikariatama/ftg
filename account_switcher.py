__version__ = (2, 0, 1)

#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://static.hikari.gay/account_switcher_icon.png
# meta banner: https://mods.hikariatama.ru/badges/account_switcher.jpg
# meta developer: @hikarimods
# scope: hikka_only
# scope: hikka_min 1.2.10

import io
import logging
import re
import typing

from aiogram.utils.exceptions import ChatNotFound
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.tl.functions.photos import UploadProfilePhotoRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import Message as TelethonMessage

from .. import loader, utils
from ..inline.types import InlineCall, InlineMessage

logger = logging.getLogger(__name__)


@loader.tds
class AccountSwitcherMod(loader.Module):
    """Allows you to easily switch between different profiles"""

    strings = {
        "name": "AccountSwitcher",
        "account_saved": (
            "<emoji document_id=5301255387306009369>🌚</emoji> <b><a"
            ' href="https://t.me/c/{}/{}">Account</a> saved!</b>'
        ),
        "restore_btn": "👆 Restore",
        "desc": "This chat will handle your saved profiles",
        "first_name_restored": (
            "<emoji document_id=5314250708508220914>✅</emoji> First name restored\n"
        ),
        "first_name_unsaved": (
            "<emoji document_id=5312383351217201533>⚠️</emoji> First name not saved\n"
        ),
        "last_name_restored": (
            "<emoji document_id=5314250708508220914>✅</emoji> First name restored\n"
        ),
        "last_name_unsaved": (
            "<emoji document_id=5312383351217201533>⚠️</emoji> First name not saved\n"
        ),
        "bio_restored": (
            "<emoji document_id=5314250708508220914>✅</emoji> Bio restored\n"
        ),
        "bio_unsaved": (
            "<emoji document_id=5312383351217201533>⚠️</emoji> Bio not saved\n"
        ),
        "data_not_restored": (
            "<emoji document_id=5312526098750252863>🚫</emoji> First name not"
            " restored\n<emoji document_id=5312526098750252863>🚫</emoji> Last name not"
            " restored\n<emoji document_id=5312526098750252863>🚫</emoji> Bio not"
            " restored\n"
        ),
        "pfp_restored": (
            "<emoji document_id=5314250708508220914>✅</emoji> Profile photo restored"
        ),
        "pfp_unsaved": (
            "<emoji document_id=5312383351217201533>⚠️</emoji> Profile photo not saved"
        ),
    }

    strings_ru = {
        "account_saved": (
            "<emoji document_id=5301255387306009369>🌚</emoji> <b><a"
            ' href="https://t.me/c/{}/{}">Аккаунт</a> сохранен!</b>'
        ),
        "restore_btn": "👆 Восстановить",
        "desc": "Тут будут появляться сохраненные профили",
        "first_name_restored": (
            "<emoji document_id=5314250708508220914>✅</emoji> Имя восстановлено\n"
        ),
        "first_name_unsaved": (
            "<emoji document_id=5312383351217201533>⚠️</emoji> Имя не сохранялось\n"
        ),
        "last_name_restored": (
            "<emoji document_id=5314250708508220914>✅</emoji> Фамилия восстановлена\n"
        ),
        "last_name_unsaved": (
            "<emoji document_id=5312383351217201533>⚠️</emoji> Фамилия не сохранялась\n"
        ),
        "bio_restored": (
            "<emoji document_id=5314250708508220914>✅</emoji> Био восстановлено\n"
        ),
        "bio_unsaved": (
            "<emoji document_id=5312383351217201533>⚠️</emoji> Био не сохранялось\n"
        ),
        "data_not_restored": (
            "<emoji document_id=5312526098750252863>🚫</emoji> Имя не"
            " восстановлено\n<emoji document_id=5312526098750252863>🚫</emoji> Фамилия"
            " не восстановлена\n<emoji document_id=5312526098750252863>🚫</emoji> Био не"
            " восстановлено\n"
        ),
        "pfp_restored": (
            "<emoji document_id=5314250708508220914>✅</emoji> Аватарка восстановлена"
        ),
        "pfp_unsaved": (
            "<emoji document_id=5312383351217201533>⚠️</emoji> Аватарка не сохранялась"
        ),
        "_cmd_doc_accsave": "Сохранить аккаунт для последующего использования",
        "_cls_doc": "Позволяет быстро переключаться между разными аккаунтами",
    }

    strings_de = {
        "account_saved": (
            "<emoji document_id=5301255387306009369>🌚</emoji> <b><a"
            ' href="https://t.me/c/{}/{}">Konto</a> gespeichert!</b>'
        ),
        "restore_btn": "👆 Wiederherstellen",
        "desc": "Dieser Chat wird deine gespeicherten Profile verwalten",
        "first_name_restored": (
            "<emoji document_id=5314250708508220914>✅</emoji> Vorname"
            " wiederhergestellt.\n"
        ),
        "first_name_unsaved": (
            "<emoji document_id=5312383351217201533>⚠️</emoji> Vorname nicht"
            " gespeichert.\n"
        ),
        "last_name_restored": (
            "<emoji document_id=5314250708508220914>✅</emoji> Nachname"
            " wiederhergestellt.\n"
        ),
        "last_name_unsaved": (
            "<emoji document_id=5312383351217201533>⚠️</emoji> Nachname nicht"
            " gespeichert.\n"
        ),
        "bio_restored": (
            "<emoji document_id=5314250708508220914>✅</emoji> Bio wiederhergestellt.\n"
        ),
        "bio_unsaved": (
            "<emoji document_id=5312383351217201533>⚠️</emoji> Bio nicht gespeichert.\n"
        ),
        "data_not_restored": (
            "<emoji document_id=5312526098750252863>🚫</emoji> Vorname nicht"
            " wiederhergestellt.\n<emoji document_id=5312526098750252863>🚫</emoji>"
            " Nachname nicht wiederhergestellt.\n<emoji"
            " document_id=5312526098750252863>🚫</emoji> Bio nicht wiederhergestellt.\n"
        ),
        "pfp_restored": (
            "<emoji document_id=5314250708508220914>✅</emoji> Profilbild"
            " wiederhergestellt."
        ),
        "pfp_unsaved": (
            "<emoji document_id=5312383351217201533>⚠️</emoji> Profilbild nicht"
            " gespeichert."
        ),
        "_cmd_doc_accsave": "Speichert das Konto für spätere Verwendung",
        "_cls_doc": "Ermöglicht es, schnell zwischen verschiedenen Konten zu wechseln",
    }

    strings_hi = {
        "account_saved": (
            "<emoji document_id=5301255387306009369>🌚</emoji> <b><a"
            ' href="https://t.me/c/{}/{}">खाता</a> सहेजा गया!</b>'
        ),
        "restore_btn": "👆 पुनर्स्थापित करें",
        "desc": "यह चैट आपके सहेजे गए प्रोफाइल का प्रबंधन करेगा",
        "first_name_restored": (
            "<emoji document_id=5314250708508220914>✅</emoji> पहला नाम पुनर्स्थापित"
            " किया गया।\n"
        ),
        "first_name_unsaved": (
            "<emoji document_id=5312383351217201533>⚠️</emoji> पहला नाम सहेजा नहीं"
            " गया।\n"
        ),
        "last_name_restored": (
            "<emoji document_id=5314250708508220914>✅</emoji> अंतिम नाम पुनर्स्थापित"
            " किया गया।\n"
        ),
        "last_name_unsaved": (
            "<emoji document_id=5312383351217201533>⚠️</emoji> अंतिम नाम सहेजा नहीं"
            " गया।\n"
        ),
        "bio_restored": (
            "<emoji document_id=5314250708508220914>✅</emoji> बायो पुनर्स्थापित किया"
            " गया।\n"
        ),
        "bio_unsaved": (
            "<emoji document_id=5312383351217201533>⚠️</emoji> बायो सहेजा नहीं गया।\n"
        ),
        "data_not_restored": (
            "<emoji document_id=5312526098750252863>🚫</emoji> पहला नाम पुनर्स्थापित"
            " नहीं किया गया।\n<emoji document_id=5312526098750252863>🚫</emoji> अंतिम"
            " नाम पुनर्स्थापित नहीं किया गया।\n<emoji"
            " document_id=5312526098750252863>🚫</emoji> बायो पुनर्स्थापित नहीं किया"
            " गया।\n"
        ),
        "pfp_restored": (
            "<emoji document_id=5314250708508220914>✅</emoji> प्रोफ़ाइल चित्र"
            " पुनर्स्थापित किया गया।"
        ),
        "pfp_unsaved": (
            "<emoji document_id=5312383351217201533>⚠️</emoji> प्रोफ़ाइल चित्र सहेजा"
            " नहीं गया।"
        ),
        "_cmd_doc_accsave": "भविष्य के उपयोग के लिए खाता सहेजें",
        "_cls_doc": "विभिन्न खातों के बीच जल्दी से जल्दी बदलने की अनुमति देता है",
    }

    strings_uz = {
        "account_saved": (
            "<emoji document_id=5301255387306009369>🌚</emoji> <b><a"
            ' href="https://t.me/c/{}/{}">Hisob</a> saqlandi!</b>'
        ),
        "restore_btn": "👆 Qayta tiklash",
        "desc": "Bu chat sizning saqlangan profilni boshqaradi",
        "first_name_restored": (
            "<emoji document_id=5314250708508220914>✅</emoji> Nomi qayta tiklandi.\n"
        ),
        "first_name_unsaved": (
            "<emoji document_id=5312383351217201533>⚠️</emoji> Nomi saqlanmadi.\n"
        ),
        "last_name_restored": (
            "<emoji document_id=5314250708508220914>✅</emoji> Familiya qayta"
            " tiklandi.\n"
        ),
        "last_name_unsaved": (
            "<emoji document_id=5312383351217201533>⚠️</emoji> Familiya saqlanmadi.\n"
        ),
        "bio_restored": (
            "<emoji document_id=5314250708508220914>✅</emoji> Bio qayta tiklandi.\n"
        ),
        "bio_unsaved": (
            "<emoji document_id=5312383351217201533>⚠️</emoji> Bio saqlanmadi.\n"
        ),
        "data_not_restored": (
            "<emoji document_id=5312526098750252863>🚫</emoji> Nomi qayta"
            " tiklanmadi.\n<emoji document_id=5312526098750252863>🚫</emoji> Familiya"
            " qayta tiklanmadi.\n<emoji document_id=5312526098750252863>🚫</emoji> Bio"
            " qayta tiklanmadi.\n"
        ),
        "pfp_restored": (
            "<emoji document_id=5314250708508220914>✅</emoji> Profil rasmi qayta"
            " tiklandi."
        ),
        "pfp_unsaved": (
            "<emoji document_id=5312383351217201533>⚠️</emoji> Profil rasmi saqlanmadi."
        ),
        "_cmd_doc_accsave": "Keyingi ishlatish uchun hisobni saqlash",
        "_cls_doc": "Tez-tez turli hisoblarga o'tishga imkon beradi",
    }

    async def client_ready(self, client, db):
        self._accs_db, is_new = await utils.asset_channel(
            self._client,
            "hikka-acc-switcher",
            self.strings("desc"),
            silent=True,
            archive=True,
            avatar="https://raw.githubusercontent.com/hikariatama/assets/master/hikka-acc-switcher.png",
            _folder="hikka",
        )

        self._accs_db_id = int(f"-100{self._accs_db.id}")

        if not is_new:
            return

        try:
            await self._client(
                InviteToChannelRequest(self._accs_db, [self.inline.bot_username])
            )
        except Exception:
            logger.warning("Unable to invite logger to chat. Maybe he's already there?")

    async def _save_acc(
        self,
        photo: typing.Optional[bytes],
        first_name: str,
        last_name: str,
        bio: str,
        no_retry: bool = False,
    ) -> int:
        info = (
            f"<code>{utils.escape_html(first_name)}</code> "
            f"<code>{utils.escape_html(last_name)}</code>\n\n"
            f"<b>Bio</b>: <code>{utils.escape_html(bio)}</code>\n"
        )

        try:
            if photo is not None:
                photo_io = io.BytesIO(photo)
                photo_io.name = "pfp.jpg"

                return (
                    await self.inline.bot.send_document(
                        self._accs_db_id,
                        photo_io,
                        caption=info,
                        parse_mode="HTML",
                        reply_markup=self.inline.generate_markup(
                            {"text": self.strings("restore_btn"), "data": "accrest"}
                        ),
                    )
                ).message_id
            else:
                return (
                    await self.inline.bot.send_message(
                        self._accs_db_id,
                        info,
                        parse_mode="HTML",
                        reply_markup=self.inline.generate_markup(
                            {"text": self.strings("restore_btn"), "data": "accrest"}
                        ),
                    )
                ).message_id
        except ChatNotFound:
            if no_retry:
                logger.exception("Can't restore account")
                return

            await self._client(
                InviteToChannelRequest(self._accs_db, [self.inline.bot_username])
            )

            return await self._save_acc(
                photo,
                first_name,
                last_name,
                bio,
                no_retry=True,
            )

    async def accrest_callback_handler(self, call: InlineCall):
        if call.data != "accrest":
            return

        await call.answer(await self._restore(call.message), show_alert=True)

    async def accsavecmd(self, message: TelethonMessage):
        """Save account for future restoring"""
        full = await self._client(GetFullUserRequest("me"))
        acc = await self._client.force_get_entity("me")

        message_id = await self._save_acc(
            (await self._client.download_profile_photo(acc, bytes))
            if full.full_user.profile_photo
            else None,
            getattr(acc, "first_name", "None"),
            getattr(acc, "last_name", "None"),
            (getattr(full.full_user, "about", "None")),
        )

        await utils.answer(
            message, self.strings("account_saved").format(self._accs_db.id, message_id)
        )

    async def _restore(
        self,
        reply: typing.Union[TelethonMessage, InlineMessage],
    ) -> str:
        log = ""

        first_name, last_name, bio = list(
            map(
                lambda x: x.replace("&gt;", ">")
                .replace("&lt;", "<")
                .replace("&quot;", '"')
                .replace("&amp;", "&"),
                re.findall(
                    r"<code>(.*?)</code>",
                    getattr(reply, "html_text", reply.text),
                    flags=re.S,
                ),
            )
        )

        if first_name == "None":
            first_name = None

        if last_name == "None":
            last_name = None

        if bio == "None":
            bio = None

        try:
            await self._client(UpdateProfileRequest(first_name, last_name, bio))

            log += (
                self.strings("first_name_restored")
                if first_name
                else self.strings("first_name_unsaved")
            )

            log += (
                self.strings("last_name_restored")
                if last_name
                else self.strings("last_name_unsaved")
            )

            log += self.strings("bio_restored") if bio else self.strings("bio_unsaved")
        except Exception:
            logger.exception("Can't restore account due to")
            log += self.strings("data_not_restored")

        try:
            upload = await self._client.upload_file(
                await self._client.download_file(reply.media, bytes)
            )
            await self._client(UploadProfilePhotoRequest(upload))
            log += self.strings("pfp_restored")
        except Exception:
            try:
                file = io.BytesIO()
                await reply.document.download(destination_file=file)

                await self._client(
                    UploadProfilePhotoRequest(
                        await self._client.upload_file(file),
                    )
                )

                log += self.strings("pfp_restored")
            except Exception:
                log += self.strings("pfp_unsaved")

        return re.sub(r"\n{2,}", "\n", log)
