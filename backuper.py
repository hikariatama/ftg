# █ █ ▀ █▄▀ ▄▀█ █▀█ ▀    ▄▀█ ▀█▀ ▄▀█ █▀▄▀█ ▄▀█
# █▀█ █ █ █ █▀█ █▀▄ █ ▄  █▀█  █  █▀█ █ ▀ █ █▀█
#
#              © Copyright 2022
#
#          https://t.me/hikariatama
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://img.icons8.com/fluency/48/000000/sync-settings.png
# meta developer: @hikariatama

from .. import loader, utils
import asyncio
import datetime
import io
import json

from telethon.tl.types import Message


@loader.tds
class BackuperMod(loader.Module):
    """Create the backup of all modules, notes, the whole database"""

    strings = {
        "name": "Backuper",
        "backup_caption": "☝️ <b>This is your database backup. Do not give it to anyone, it contains personal info.</b>",
        "reply_to_file": "🚫 <b>Reply to .{} file</b>",
        "db_restored": "🔄 <b>Database updated, restarting...</b>",
        "modules_backup": "🗃 <b>Backup mods ({})</b>",
        "notes_backup": "🗃 <b>Backup notes ({})</b>",
        "mods_restored": "✅ <b>Modes restored, restarting</b>",
        "notes_restored": "✅ <b>Notes restored</b>",
    }

    async def client_ready(self, client, db):
        self._db = db
        self._client = client

    async def backupdbcmd(self, message: Message):
        """Create database backup [will be sent in pm]"""
        txt = io.BytesIO(json.dumps(self._db).encode("utf-8"))
        txt.name = f"db-backup-{getattr(datetime, 'datetime', datetime).now().strftime('%d-%m-%Y-%H-%M')}.db"
        await self._client.send_file("me", txt, caption=self.strings("backup_caption"))
        await message.delete()

    async def restoredbcmd(self, message: Message):
        """Restore database from file"""
        reply = await message.get_reply_message()
        if not reply or not reply.media:
            await utils.answer(
                message,
                self.strings("reply_to_file").format("db"),
            )
            await asyncio.sleep(3)
            await message.delete()
            return

        file = await self._client.download_file(reply.media, bytes)
        decoded_text = json.loads(file.decode("utf-8"))
        self._db.clear()
        self._db.update(**decoded_text)
        self._db.save()
        # print(decoded_text)
        await utils.answer(message, self.strings("db_restored"))
        await self.allmodules.commands["restart"](await message.respond("_"))

    async def backupmodscmd(self, message: Message):
        """Create backup of mods"""
        data = json.dumps(self._db.get("hikka.modules.loader", "loaded_modules", {}))
        txt = io.BytesIO(data.encode("utf-8"))
        txt.name = f"mods-{getattr(datetime, 'datetime', datetime).now().strftime('%d-%m-%Y-%H-%M')}.mods"
        await self._client.send_file(
            utils.get_chat_id(message),
            txt,
            caption=self.strings("modules_backup").format(
                len(self._db.get("hikka.modules.loader", "loaded_modules", {}))
            ),
        )
        await message.delete()

    async def restoremodscmd(self, message: Message):
        """<reply to file> - Restore mods from backup"""
        reply = await message.get_reply_message()
        if not reply or not reply.media:
            await utils.answer(message, self.strings("reply_to_file").format("mods"))
            await asyncio.sleep(3)
            await message.delete()
            return

        file = await self._client.download_file(reply.media, bytes)
        decoded_text = json.loads(file.decode("utf-8"))
        self._db.set(
            "hikka.modules.loader",
            "loaded_modules",
            decoded_text["loaded"],
        )
        self._db.save()
        await utils.answer(message, self.strings("mods_restored"))
        await self.allmodules.commands["restart"](await message.respond("_"))

    async def backupnotescmd(self, message: Message):
        """Create the backup of notes"""
        data = json.dumps(self._db.get("hikka.modules.notes", "notes", []))
        txt = io.BytesIO(data.encode("utf-8"))
        txt.name = f"notes-{getattr(datetime, 'datetime', datetime).now().strftime('%d-%m-%Y-%H-%M')}.notes"
        await self._client.send_file(
            utils.get_chat_id(message),
            txt,
            caption=self.strings("notes_backup").format(
                len(self._db.get("hikka.modules.notes", "notes", []))
            ),
        )
        await message.delete()

    async def restorenotescmd(self, message: Message):
        """<reply to file> - Restore notes from backup"""
        reply = await message.get_reply_message()
        if not reply or not reply.media:
            await utils.answer(message, self.strings("reply_to_file").format("notes"))
            await asyncio.sleep(3)
            await message.delete()
            return

        file = await self._client.download_file(reply.media, bytes)
        decoded_text = json.loads(file.decode("utf-8"))
        self._db.set("hikka.modules.notes", "notes", decoded_text)
        self._db.save()
        await utils.answer(message, self.strings("notes_restored"))
