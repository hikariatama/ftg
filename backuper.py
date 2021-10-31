"""
    Copyright 2021 t.me/innocoffee
    Licensed under the Apache License, Version 2.0
    
    Author is not responsible for any consequencies caused by using this
    software or any of its parts. If you have any questions or wishes, feel
    free to contact Dan by sending pm to @innocoffee_alt.
"""

#<3 title: Backuper
#<3 pic: https://img.icons8.com/fluency/48/000000/sync-settings.png
#<3 desc: Сделать резервную копию базы данных FTG, а в будущем и всех модулей, заметок и др.

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
    strings = {"name":"Backuper"}

    async def client_ready(self, client, db):
        self.db = db
        self.client = client

    async def backupdbcmd(self, message):
        """.backupdb - Создать бекап базы данных фтг"""
        txt = io.BytesIO(json.dumps(self.db).encode('utf-8'))
        txt.name = f"ftg-db-backup-{datetime.datetime.now().strftime('%d-%m-%Y-%H-%M')}.db"
        await self.client.send_file('me', txt)
        await self.client.send_message('me', '☝️ <b>Это - бекап базы данных. Никому его не передавай</b>')
        await message.delete()

    async def restoredbcmd(self, message):
        """.restoredb <key> - Восстановить базу данных из файла"""
        reply = await message.get_reply_message()
        if not reply or not reply.media:
            await utils.answer(message, '<b>Reply to .db file</b>')
            await asyncio.sleep(3)
            await message.delete()
            return

        file = await message.client.download_file(reply.media)
        decoded_text = json.loads(file.decode('utf-8'))
        self.db.clear()
        self.db.update(**decoded_text)
        self.db.save()
        # print(decoded_text)
        await utils.answer(message, '<b>База данных обновлена. Перезапускаю юзербот...</b>')
        await self.allmodules.commands['restart'](await message.respond('_'))

    async def washdbcmd(self, message):
        """.wasdb <arg> - Помыть базу данных
        -1 --filemods - Убрать конфиги модулей, загруженных из файла
        -2 --deadrepos - Убрать мертвые репозитории
        -3 --refactorrepos - Заменить ссылки githubusercontent ссылки на нормальные
        -4 --deleteconf - Удалить конфиги выгруженных модулей
        -a --all - Применить все фильтры"""

        await self.backupdbcmd(await message.respond('_'))

        args = utils.get_args_raw(message)

        if '-a' in args or '--all' in args:
            args = '-1 -2 -3 -4'

        res = ""
        if '--filemods' in args or '-1' in args:
            todel = []
            for x in self.db.keys(): 
                if "__extmod" in x:
                    todel.append(x)

            for delete in todel:
                self.db.pop(delete)

            res += f"\n✅ Удалено {len(todel)} конфигов модулей, загруженных из файла"

        if '--deadrepos' in args or '-2' in args:
            counter = 0
            mods = []
            for mod in self.db.get("friendly-telegram.modules.loader", "loaded_modules"):
                if ('http://' in mod or 'https://' in mod) and requests.get(mod).status_code == 404:
                    counter += 1
                else:
                    mods.append(mod)

            self.db.set('friendly-telegram.modules.loader', 'loaded_modules', mods)
            res += f"\n✅ Удалено {counter} мертвых репо"

        if '--refactorrepos' in args or '-3' in args:
            counter = json.dumps(self.db).count('githubusercontent')
            mods = re.sub(r'http[s]?:\/\/raw\.githubusercontent\.com\/([^\/]*?\/[^\/]*?)(\/[^\"\']*)', r'https://github.com/\1/raw\2', re.sub(r'http[s]?:\/\/raw%dgithubusercontent%dcom\/([^\/]*?\/[^\/]*?)(\/[^\"\']*)', r'https://github%dcom/\1/raw\2', json.dumps(self.db), flags=re.S), flags=re.S)
            self.db.clear()
            self.db.update(**json.loads(mods))

            res += f"\n✅ Заменено {counter} мертвых репо"

        if '--deleteconf' in args or '-4' in args:
            counter = 0
            todel = []
            for x in self.db.keys(): 
                if x.startswith('friendly-telegram.modules.'):
                    link = x.split('.', 3)[2].replace('%d', '.')
                    if link not in self.db.get("friendly-telegram.modules.loader", "loaded_modules") and link != 'loader':
                        todel.append(x)

            for delete in todel:
                self.db.pop(delete)


            res += f"\n✅ Удалено {len(todel)} конфигов выгруженных модулей"

        self.db.save()
        await utils.answer(message, res)


