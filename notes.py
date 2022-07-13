#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# scope: hikka_min 1.2.10

# meta pic: https://img.icons8.com/tiny-color/256/000000/experimental-note-tiny-color.png
# meta developer: @hikarimods

import logging

from telethon.tl.types import Message  # noqa

from .. import loader, utils  # noqa

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

    async def client_ready(self, client, db):
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
