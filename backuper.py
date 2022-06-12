# █ █ ▀ █▄▀ ▄▀█ █▀█ ▀    ▄▀█ ▀█▀ ▄▀█ █▀▄▀█ ▄▀█
# █▀█ █ █ █ █▀█ █▀▄ █ ▄  █▀█  █  █▀█ █ ▀ █ █▀█
#
#              © Copyright 2022
#
#          https://t.me/hikariatama
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://img.icons8.com/stickers/500/000000/data-backup.png
# meta developer: @hikarimods
# scope: hikka_only
# scope: hikka_min 1.1.15

import datetime
import io
import json
import logging
import os
import zipfile

from telethon.tl.types import Message

from .. import loader, utils

logger = logging.getLogger(__name__)

DATA_DIR = (
    os.path.normpath(os.path.join(utils.get_base_dir(), ".."))
    if "OKTETO" not in os.environ and "DOCKER" not in os.environ
    else "/data"
)

LOADED_MODULES_DIR = os.path.join(DATA_DIR, "loaded_modules")


@loader.tds
class BackuperMod(loader.Module):
    """Create the backup of all modules or the whole database"""

    strings = {
        "name": "Backuper",
        "backup_caption": "☝️ <b>This is your database backup. Do not give it to anyone, it contains personal info.</b>",
        "reply_to_file": "🚫 <b>Reply to .json or .zip file</b>",
        "db_restored": "🔄 <b>Database updated, restarting...</b>",
        "modules_backup": "🗃 <b>Backup mods ({})</b>",
        "mods_restored": "✅ <b>Mods restored, restarting</b>",
    }

    strings_ru = {
        "backup_caption": "☝️ <b>Это - бекап базы данных. Никому его не передавай, он содержит личную информацию.</b>",
        "reply_to_file": "🚫 <b>Ответь на .json или .zip файл</b>",
        "db_restored": "🔄 <b>База обновлена, перезагружаюсь...</b>",
        "modules_backup": "🗃 <b>Бекап модулей ({})</b>",
        "mods_restored": "✅ <b>Модули восстановлены, перезагружаюсь</b>",
        "_cmd_doc_backupdb": "Создать бекап базы данных [будет отправлен в Избранное]",
        "_cmd_doc_restoredb": "Восстановить базу данных из файла",
        "_cmd_doc_backupmods": "Создать бекап модулей",
        "_cmd_doc_restoremods": "<reply to file> - Восстановить модули из файла",
        "_cls_doc": "Создает резервные копии",
    }

    async def client_ready(self, client, db):
        self._db = db
        self._client = client

    async def backupdbcmd(self, message: Message):
        """Create database backup [will be sent in pm]"""
        txt = io.BytesIO(json.dumps(self._db).encode("utf-8"))
        txt.name = f"db-backup-{getattr(datetime, 'datetime', datetime).now().strftime('%d-%m-%Y-%H-%M')}.json"
        await self._client.send_file("me", txt, caption=self.strings("backup_caption"))
        await message.delete()

    async def restoredbcmd(self, message: Message):
        """Restore database from file"""
        reply = await message.get_reply_message()
        if not reply or not reply.media:
            await utils.answer(
                message,
                self.strings("reply_to_file"),
            )
            return

        file = await self._client.download_file(reply.media, bytes)
        decoded_text = json.loads(file.decode("utf-8"))

        if not self._db.process_db_autofix(decoded_text):
            raise RuntimeError("Attempted to restore broken database")

        self._db.clear()
        self._db.update(**decoded_text)
        self._db.save()
        await utils.answer(message, self.strings("db_restored"))
        await self.allmodules.commands["restart"](
            await message.respond(f"{self.get_prefix()}restart --force")
        )

    async def backupmodscmd(self, message: Message):
        """Create backup of mods"""
        mods_quantity = len(self.lookup("Loader").get("loaded_modules", {}))

        result = io.BytesIO()
        result.name = "mods.zip"

        db_mods = json.dumps(self.lookup("Loader").get("loaded_modules", {})).encode()

        with zipfile.ZipFile(result, "w", zipfile.ZIP_DEFLATED) as zipf:
            if "DYNO" not in os.environ:
                for root, _, files in os.walk(LOADED_MODULES_DIR):
                    for file in files:
                        with open(os.path.join(root, file), "rb") as f:
                            zipf.writestr(file, f.read())
                            mods_quantity += 1

            zipf.writestr("db_mods.json", db_mods)

        archive = io.BytesIO(result.getvalue())
        archive.name = f"mods-{getattr(datetime, 'datetime', datetime).now().strftime('%d-%m-%Y-%H-%M')}.zip"

        await self._client.send_file(
            utils.get_chat_id(message),
            archive,
            caption=self.strings("modules_backup").format(mods_quantity),
        )
        await message.delete()

    async def restoremodscmd(self, message: Message):
        """<reply to file> - Restore mods from backup"""
        reply = await message.get_reply_message()
        if not reply or not reply.media:
            await utils.answer(message, self.strings("reply_to_file"))
            return

        file = await self._client.download_file(reply.media, bytes)
        try:
            decoded_text = json.loads(file.decode("utf-8"))
        except Exception:
            try:
                file = io.BytesIO(file)
                file.name = "mods.zip"

                with zipfile.ZipFile(file) as zf:
                    for name in zf.namelist():
                        with zf.open(name, "r") as module:
                            if name == "db_mods.json":
                                db_mods = json.loads(module.read().decode())
                                if isinstance(db_mods, dict) and all(
                                    isinstance(key, str) and isinstance(value, str)
                                    for key, value in db_mods.items()
                                ):
                                    self.lookup("Loader").set("loaded_modules", db_mods)

                                continue

                            if "DYNO" not in os.environ:
                                with open(
                                    os.path.join(LOADED_MODULES_DIR, name), "wb"
                                ) as f:
                                    f.write(module.read())
            except Exception:
                logger.exception("Can't restore mods")
                await utils.answer(message, self.strings("reply_to_file"))
                return
        else:
            if not isinstance(decoded_text, dict) or not all(
                isinstance(key, str) and isinstance(value, str)
                for key, value in decoded_text.items()
            ):
                raise RuntimeError("Invalid backup")

            self.lookup("Loader").set("loaded_modules", decoded_text)

        await utils.answer(message, self.strings("mods_restored"))
        await self.allmodules.commands["restart"](
            await message.respond(f"{self.get_prefix()}restart --force")
        )
