"""
    Copyright 2021 t.me/innocoffee
    Licensed under the Apache License, Version 2.0
    
    Author is not responsible for any consequencies caused by using this
    software or any of its parts. If you have any questions or wishes, feel
    free to contact Dan by sending pm to @innocoffee_alt.
"""

#<3 title: MagicBroom
#<3 pic: https://img.icons8.com/fluency/48/000000/broom.png
#<3 desc: Волшебная метла выметет весь хлам из твоей телеги

from .. import loader, utils
import asyncio
import re
import telethon
import requests
import json


@loader.tds
class MagicBroomMod(loader.Module):
    """Волшебная метла выметет весь хлам из твоей телеги"""
    strings = {'name': 'MagicBroom',
    'no_args': "🦊 <b>Необходимо указать аргументы </b><code>.help MagicBroom</code>",
    'will_be_removed': '<b>🦊 Будет удалено {} диалогов:</b>\n<pre>   🔸 {}</pre>\n\n🔰 Команда: <code>.broom {}</code>', 
    'nothing_will_be_removed': '<b>🦊 Ни один чат не будет удален</b>', 
    'fuck_off': '🦊 <b>Я не хочу никаких сообщений от тебя, поэтому ты заблокирован.</b>',
    'removed': '<b>🦊 Удалено {} диалогов:</b>\n<pre>   🔸 {}</pre>',
    'nothing_removed': '<b>🦊 Ни одного чата не было удалено</b>', 
    'broom_file': "\n✅ Удалено {} конфигов модулей, загруженных из файла", 
    'broom_deadrepos': "\n✅ Удалено {} мертвых репо", 
    'broom_refactorrepos': "\n✅ Заменено {} старых репо", 
    'broom_deletedconfs': "\n✅ Удалено {} конфигов выгруженных модулей"
    }
    
    async def client_ready(self, client, db):
        self.db = db
        self.client = client

    async def broom(self, message):
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings('no_args', message))
            await asyncio.sleep(3)
            await message.delete()
            return False

        deleted, restricted, scam, query = False, False, False, False

        if '-d' in args:
            args = args.replace('-d', '').replace('  ', ' ')
            deleted = True
        
        if '-b' in args:
            args = args.replace('-b', '').replace('  ', ' ')
            restricted = True
        
        if '-s' in args:
            args = args.replace('-s', '').replace('  ', ' ')
            scam = True

        if '-q' in args:
            query = re.search(r'-q [\'"]?([^ ]*)[\'"]?', args).group(1)

        dialogs = await self.client.get_dialogs()
        todel = []
        for dialog in dialogs:
            if 'friendly' in dialog.name.lower():
                continue

            if scam and getattr(dialog.entity, "scam", False) or restricted and getattr(dialog.entity, "restricted", False) or deleted and getattr(dialog.entity, "deleted", False) or query and (query.lower() in dialog.name.lower() or re.match(query, dialog.name) is not None):
                todel.append(dialog)

        return todel

    async def broompcmd(self, message):
        """.broomp <args> - Волшебная чистка телеги (предпросмотр чатов, которые будут удалены)"""
        ans = await self.broom(message)
        if ans is False:
            return
        if len(ans) > 0:
            chats = "\n   🔸 ".join([d.name for d in ans])
            await utils.answer(message, self.strings('will_be_removed', message).format(len(ans), chats, message.text[7:]))
        else:
            await utils.answer(message, self.strings('nothing_will_be_removed', message))

    async def broomcmd(self, message):
        """.broom <args> - Волшебная чистка телеги
        -d - Удалить переписки с удаленными аккаунтами
        -b - Удалить переписки с заблокированными аккаунтами
        -s - Удалить переписки со скам аккаунтами
        -q <поисковый запрос> - Удалить переписки, соответствующие запросу"""
        ans = await self.broom(message)
        if ans is False:
            return

        [await self.client.delete_dialog(d.entity) for d in ans]
        if len(ans) > 0:
            chats = "\n   🔸 ".join([d.name for d in ans])
            await utils.answer(message, self.strings('removed', message).format(len(ans), chats))
        else:
            await utils.answer(message, self.strings('nothing_removed', message))


    async def washdbcmd(self, message):
        """.wasdb <arg> - Помыть базу данных (рекомендуется .backupdb)
        -1 --filemods - Убрать конфиги модулей, загруженных из файла
        -2 --deadrepos - Убрать мертвые репозитории
        -3 --refactorrepos - Заменить ссылки githubusercontent ссылки на нормальные
        -4 --deleteconf - Удалить конфиги выгруженных модулей
        -a --all - Применить все фильтры"""

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

            res += self.strings('broom_file', message).format(len(todel))

        if '--deadrepos' in args or '-2' in args:
            counter = 0
            mods = []
            for mod in self.db.get("friendly-telegram.modules.loader", "loaded_modules"):
                if ('http://' in mod or 'https://' in mod) and requests.get(mod).status_code == 404:
                    counter += 1
                else:
                    mods.append(mod)

            self.db.set('friendly-telegram.modules.loader', 'loaded_modules', mods)
            res += self.strings('broom_deadrepos', message).format(counter)

        if '--refactorrepos' in args or '-3' in args:
            counter = json.dumps(self.db).count('githubusercontent')
            mods = re.sub(r'http[s]?:\/\/raw\.githubusercontent\.com\/([^\/]*?\/[^\/]*?)(\/[^\"\']*)', r'https://github.com/\1/raw\2', re.sub(r'http[s]?:\/\/raw%dgithubusercontent%dcom\/([^\/]*?\/[^\/]*?)(\/[^\"\']*)', r'https://github%dcom/\1/raw\2', json.dumps(self.db), flags=re.S), flags=re.S)
            self.db.clear()
            self.db.update(**json.loads(mods))

            res += self.strings('broom_refactorrepos', message).format(counter)

        if '--deleteconf' in args or '-4' in args:
            todel = []
            for x in self.db.keys(): 
                if x.startswith('friendly-telegram.modules.'):
                    link = x.split('.', 3)[2].replace('%d', '.')
                    if link not in self.db.get("friendly-telegram.modules.loader", "loaded_modules") and link != 'loader':
                        todel.append(x)

            for delete in todel:
                self.db.pop(delete)


            res += self.strings('broom_deletedconfs', message).format(len(todel))

        self.db.save()
        await utils.answer(message, res)


    async def pbancmd(self, message):
        """.pban <в чате> <args> - Удаляет чат \\ блокирует бота \\ блокирует человека
        -h - Удалить историю
        -hh - Удалить историю для обоих собеседников"""
        args = utils.get_args_raw(message)
        entity = await self.client.get_entity(message.peer_id)
        if type(entity) is telethon.tl.types.User:
            try:
                if '-hh' in args:
                    await self.client(telethon.tl.functions.messages.DeleteHistoryRequest(
                        peer=entity, 
                        just_clear=False,
                        revoke=True,
                        max_id=0
                    ))
                elif '-h' in args:
                    await self.client(telethon.tl.functions.messages.DeleteHistoryRequest(
                        peer=entity, 
                        just_clear=True,
                        max_id=0
                    ))
                    await self.client.send_message(utils.get_chat_id(message), self.strings('fuck_off', message))
                else:
                    await self.client.send_message(utils.get_chat_id(message), self.strings('fuck_off', message))
            except:
                pass

            await self.client(telethon.tl.functions.contacts.BlockRequest(
                id=entity
            ))
        else:
            await self.client.delete_dialog(entity)
