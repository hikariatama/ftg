#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://static.dan.tatar/notes_icon.png
# meta banner: https://mods.hikariatama.ru/badges/notes.jpg
# meta developer: @hikarimods
# scope: hikka_only
# scope: hikka_min 1.2.10

import logging

from telethon.tl.types import Message

from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class NotesMod(loader.Module):
    """Advanced notes module with folders and other features"""

    strings = {
        "name": "Notes",
        "saved": (
            "💾 <b>Saved note with name </b><code>{}</code>.\nFolder:"
            " </b><code>{}</code>.</b>"
        ),
        "no_reply": "🚫 <b>Reply and note name are required.</b>",
        "no_name": "🚫 <b>Specify note name.</b>",
        "no_note": "🚫 <b>Note not found.</b>",
        "available_notes": "💾 <b>Current notes:</b>\n",
        "no_notes": "😔 <b>You have no notes yet</b>",
        "deleted": "🙂 <b>Deleted note </b><code>{}</code>",
    }

    strings_ru = {
        "saved": (
            "💾 <b>Заметка с именем </b><code>{}</code><b> сохранена</b>.\nПапка:"
            " </b><code>{}</code>.</b>"
        ),
        "no_reply": "🚫 <b>Требуется реплай на контент заметки.</b>",
        "no_name": "🚫 <b>Укажи имя заметки.</b>",
        "no_note": "🚫 <b>Заметка не найдена.</b>",
        "available_notes": "💾 <b>Текущие заметки:</b>\n",
        "no_notes": "😔 <b>У тебя пока что нет заметок</b>",
        "deleted": "🙂 <b>Заметка с именем </b><code>{}</code> <b>удалена</b>",
        "_cmd_doc_hsave": "[папка] <имя> - Сохранить заметку",
        "_cmd_doc_hget": "<имя> - Показать заметку",
        "_cmd_doc_hdel": "<имя> - Удалить заметку",
        "_cmd_doc_hlist": "[папка] - Показать все заметки",
        "_cls_doc": "Модуль заметок с расширенным функционалом. Папки и категории",
    }

    strings_de = {
        "saved": (
            "💾 <b>Notiz mit dem Namen </b><code>{}</code><b> gespeichert</b>.\nOrdner:"
            " </b><code>{}</code>.</b>"
        ),
        "no_reply": "🚫 <b>Antworte auf den Inhalt der Notiz.</b>",
        "no_name": "🚫 <b>Gib einen Namen für die Notiz an.</b>",
        "no_note": "🚫 <b>Notiz nicht gefunden.</b>",
        "available_notes": "💾 <b>Aktuelle Notizen:</b>\n",
        "no_notes": "😔 <b>Du hast noch keine Notizen</b>",
        "deleted": "🙂 <b>Notiz mit dem Namen </b><code>{}</code> <b>gelöscht</b>",
        "_cmd_doc_hsave": "[Ordner] <Name> - Speichert eine neue Notiz",
        "_cmd_doc_hget": "<Name> - Zeigt eine Notiz an",
        "_cmd_doc_hdel": "<Name> - Löscht eine Notiz",
        "_cmd_doc_hlist": "[Ordner] - Zeigt alle Notizen an",
        "_cls_doc": "Notizenmodul mit erweiterten Funktionen. Ordner und Kategorien",
    }

    strings_tr = {
        "saved": (
            "💾 <b>Notu adı </b><code>{}</code><b> kaydedildi</b>.\nKlasör:"
            " </b><code>{}</code>.</b>"
        ),
        "no_reply": "🚫 <b>Not içeriğine yanıt verin.</b>",
        "no_name": "🚫 <b>Bir not adı belirtin.</b>",
        "no_note": "🚫 <b>Not bulunamadı.</b>",
        "available_notes": "💾 <b>Mevcut notlar:</b>\n",
        "no_notes": "😔 <b>Henüz notunuz yok</b>",
        "deleted": "🙂 <b>Not adı </b><code>{}</code> <b>silindi</b>",
        "_cmd_doc_hsave": "[Klasör] <Ad> - Yeni bir not kaydedin",
        "_cmd_doc_hget": "<Ad> - Bir notu göster",
        "_cmd_doc_hdel": "<Ad> - Bir notu sil",
        "_cmd_doc_hlist": "[Klasör] - Tüm notları göster",
        "_cls_doc": "Gelişmiş not modülü. Klasörler ve diğer özellikler",
    }

    strings_uz = {
        "saved": (
            "💾 <b>Qayd nomi </b><code>{}</code><b> saqlandi</b>.\nJild:"
            " </b><code>{}</code>.</b>"
        ),
        "no_reply": "🚫 <b>Qayd tarkibiga javob bering.</b>",
        "no_name": "🚫 <b>Qayd nomini kiriting.</b>",
        "no_note": "🚫 <b>Qayd topilmadi.</b>",
        "available_notes": "💾 <b>Mavjud qaydlar:</b>\n",
        "no_notes": "😔 <b>Hozircha sizda qayd yo'q</b>",
        "deleted": "🙂 <b>Qayd nomi </b><code>{}</code> <b>o'chirildi</b>",
        "_cmd_doc_hsave": "[Jild] <Nomi> - Yangi qayd saqlash",
        "_cmd_doc_hget": "<Nomi> - Qaydni ko'rsatish",
        "_cmd_doc_hdel": "<Nomi> - Qaydni o'chirish",
        "_cmd_doc_hlist": "[Jild] - Barcha qaydlarni ko'rsatish",
        "_cls_doc": "Kengaytirilgan qayd moduli. Jildlar va kategoriyalar",
    }

    strings_hi = {
        "saved": (
            "💾 <b>नोट का नाम </b><code>{}</code><b> सहेजा गया</b>.\nफ़ोल्डर:"
            " </b><code>{}</code>.</b>"
        ),
        "no_reply": "🚫 <b>नोट की अंतर्दृष्टि पर जवाब दें।</b>",
        "no_name": "🚫 <b>एक नोट नाम दर्ज करें।</b>",
        "no_note": "🚫 <b>नोट नहीं मिला।</b>",
        "available_notes": "💾 <b>उपलब्ध नोट्स:</b>\n",
        "no_notes": "😔 <b>आपके पास अभी तक कोई नोट नहीं है</b>",
        "deleted": "🙂 <b>नोट नाम </b><code>{}</code> <b>हटा दिया गया</b>",
        "_cmd_doc_hsave": "[फ़ोल्डर] <नाम> - एक नया नोट सहेजें",
        "_cmd_doc_hget": "<नाम> - एक नोट दिखाएं",
        "_cmd_doc_hdel": "<नाम> - एक नोट हटाएं",
        "_cmd_doc_hlist": "[फ़ोल्डर] - सभी नोट्स दिखाएं",
        "_cls_doc": "उन्नत नोट्स मॉड्यूल। फ़ोल्डर और श्रेणियाँ",
    }

    async def client_ready(self):
        self._notes = self.get("notes", {})

    async def hsavecmd(self, message: Message):
        """[folder] <name> - Save new note"""
        args = utils.get_args_raw(message)

        if len(args.split()) >= 2:
            folder = args.split()[0]
            args = args.split(maxsplit=1)[1]
        else:
            folder = "global"

        reply = await message.get_reply_message()

        if not (reply and args):
            await utils.answer(message, self.strings("no_reply"))
            return

        if folder not in self._notes:
            self._notes[folder] = {}
            logger.warning(f"Created new folder {folder}")

        asset = await self._db.store_asset(reply)

        if getattr(reply, "video", False):
            type_ = "🎞"
        elif getattr(reply, "photo", False):
            type_ = "🖼"
        elif getattr(reply, "voice", False):
            type_ = "🗣"
        elif getattr(reply, "audio", False):
            type_ = "🎧"
        elif getattr(reply, "file", False):
            type_ = "📝"
        else:
            type_ = "🔹"

        self._notes[folder][args] = {"id": asset, "type": type_}

        self.set("notes", self._notes)

        await utils.answer(message, self.strings("saved").format(args, folder))

    def _get_note(self, name):
        for category, notes in self._notes.items():
            for note, asset in notes.items():
                if note == name:
                    return asset

    def _del_note(self, name):
        for category, notes in self._notes.copy().items():
            for note, asset in notes.copy().items():
                if note == name:
                    del self._notes[category][note]

                    if not self._notes[category]:
                        del self._notes[category]

                    self.set("notes", self._notes)
                    return True

        return False

    async def hgetcmd(self, message: Message):
        """<name> - Show specified note"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings("no_name"))
            return

        asset = self._get_note(args)
        if not asset:
            await utils.answer(message, self.strings("no_note"))
            return

        await self._client.send_message(
            message.peer_id,
            await self._db.fetch_asset(asset["id"]),
            reply_to=getattr(message, "reply_to_msg_id", False),
        )

        if message.out:
            await message.delete()

    async def hdelcmd(self, message: Message):
        """<name> - Delete specified note"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings("no_name"))
            return

        asset = self._get_note(args)
        if not asset:
            await utils.answer(message, self.strings("no_note"))
            return

        try:
            await (await self._db.fetch_asset(asset["id"])).delete()
        except Exception:
            pass

        self._del_note(args)

        await utils.answer(message, self.strings("deleted").format(args))

    async def hlistcmd(self, message: Message):
        """[folder] - List all notes"""
        args = utils.get_args_raw(message)

        if not self._notes:
            await utils.answer(message, self.strings("no_notes"))
            return

        result = self.strings("available_notes")

        if not args or args not in self._notes:
            for category, notes in self._notes.items():
                result += f"\n🔸 <b>{category}</b>\n"
                for note, asset in notes.items():
                    result += f"    {asset['type']} <code>{note}</code>\n"

            await utils.answer(message, result)
            return

        for note, asset in self._notes[args].items():
            result += f"{asset['type']} <code>{note}</code>\n"

        await utils.answer(message, result)
