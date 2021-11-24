"""
    Copyright 2021 t.me/innocoffee
    Licensed under the Apache License, Version 2.0
    
    Author is not responsible for any consequencies caused by using this
    software or any of its parts. If you have any questions or wishes, feel
    free to contact Dan by sending pm to @innocoffee_alt.
"""

#<3 title: Backuper
#<3 pic: https://img.icons8.com/fluency/48/000000/sync-settings.png
#<3 desc: Сделать резервную копию базы данных FTG, модулей, заметок и др. Почистить базу данных от мертвых репо и другого хлама

from .. import loader, utils
import asyncio
import datetime
import io
import json
import requests
import re

@loader.tds
class BackuperMod(loader.Module):
    """Backup everything and anything"""
    strings = {"name":"Backuper",
    'backup_caption': '☝️ <b>Это - бекап базы данных. Никому его не передавай</b>', 
    'reply_to_file': '<b>Reply to .{} file</b>', 
    'db_restored': '<b>База данных обновлена. Перезапускаю юзербот...</b>', 
    'modules_backup': '🦊 <b>Резервная копия модулей ({})</b>',
    'notes_backup': '🦊 <b>Резервная копия заметок ({})</b>', 
    'mods_restored': '🦊 <b>Моды восстановлены, перезагружаюсь</b>', 
    'notes_restored': '🦊 <b>Заметки восстановлены</b>'}

    async def client_ready(self, client, db):
        self.db = db
        self.client = client

    async def backupdbcmd(self, message):
        """Создать бекап базы данных фтг"""
        txt = io.BytesIO(json.dumps(self.db).encode('utf-8'))
        txt.name = f"ftg-db-backup-{datetime.datetime.now().strftime('%d-%m-%Y-%H-%M')}.db"
        await self.client.send_file('me', txt, caption=self.strings('backup_caption'))
        await message.delete()

    async def restoredbcmd(self, message):
        """<key> - Восстановить базу данных из файла"""
        reply = await message.get_reply_message()
        if not reply or not reply.media:
            await utils.answer(message, self.strings('reply_to_file', message).format('db'))
            await asyncio.sleep(3)
            await message.delete()
            return

        file = await message.client.download_file(reply.media)
        decoded_text = json.loads(file.decode('utf-8'))
        self.db.clear()
        self.db.update(**decoded_text)
        self.db.save()
        # print(decoded_text)
        await utils.answer(message, self.strings('db_restored', message))
        await self.allmodules.commands['restart'](await message.respond('_'))


    async def backupmodscmd(self, message):
        """Сделать резервную копию загруженных и выгруженных модулей"""
        data = json.dumps({'loaded': self.db.get("friendly-telegram.modules.loader", "loaded_modules", []), 'unloaded': self.db.get("friendly-telegram.modules.loader", "unloaded_modules", [])})
        txt = io.BytesIO(data.encode('utf-8'))
        txt.name = f"ftg-mods-{datetime.datetime.now().strftime('%d-%m-%Y-%H-%M')}.mods"
        await self.client.send_file(utils.get_chat_id(message), txt, caption=self.strings('modules_backup', message).format(len(self.db.get("friendly-telegram.modules.loader", "loaded_modules", []))))
        await message.delete()

    async def restoremodscmd(self, message):
        """<reply to file> - Восстановить моды из резервной копии"""
        reply = await message.get_reply_message()
        if not reply or not reply.media:
            await utils.answer(message, self.strings('reply_to_file', message).format('mods'))
            await asyncio.sleep(3)
            await message.delete()
            return

        file = await message.client.download_file(reply.media)
        decoded_text = json.loads(file.decode('utf-8'))
        self.db.set("friendly-telegram.modules.loader", "loaded_modules", decoded_text['loaded'])
        self.db.set("friendly-telegram.modules.loader", "unloaded_modules", decoded_text['unloaded'])
        self.db.save()
        await utils.answer(message, self.strings('mods_restored', message))
        await self.allmodules.commands['restart'](await message.respond('_'))

    async def backupnotescmd(self, message):
        """Сделать резервную копию заметок"""
        data = json.dumps(self.db.get("friendly-telegram.modules.notes", "notes", []))
        txt = io.BytesIO(data.encode('utf-8'))
        txt.name = f"ftg-notes-{datetime.datetime.now().strftime('%d-%m-%Y-%H-%M')}.notes"
        await self.client.send_file(utils.get_chat_id(message), txt, caption=self.strings('notes_backup', message).format(len(self.db.get("friendly-telegram.modules.notes", "notes", []))))
        await message.delete()

    async def restorenotescmd(self, message):
        """<reply to file> - Восстановить заметки из резервной копии"""
        reply = await message.get_reply_message()
        if not reply or not reply.media:
            await utils.answer(message, self.strings('reply_to_file', message).format('notes'))
            await asyncio.sleep(3)
            await message.delete()
            return

        file = await message.client.download_file(reply.media)
        decoded_text = json.loads(file.decode('utf-8'))
        self.db.set("friendly-telegram.modules.notes", "notes", decoded_text)
        self.db.save()
        await utils.answer(message, self.strings('notes_restored', message))


