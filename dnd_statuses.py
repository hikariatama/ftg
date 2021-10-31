"""
    Copyright 2021 t.me/innocoffee
    Licensed under the Apache License, Version 2.0
    
    Author is not responsible for any consequencies caused by using this
    software or any of its parts. If you have any questions or wishes, feel
    free to contact Dan by sending pm to @innocoffee_alt.
"""

"""

    THIS VERSION IS ONLY FOR BETA TESTING
    DO NOT LOAD IT

"""

#<3 title: Statuses
#<3 pic: https://img.icons8.com/fluency/48/000000/envelope-number.png
#<3 desc: Установить статус, отключить уведомления

from .. import loader, utils
import asyncio
from telethon import types

@loader.tds
class statusesMod(loader.Module):
    strings = {"name": "Statuses", 
    'status_not_found': '<b>🦊 Статус не найден</b>',
    'status_set': '<b>🦊 Статус установлен\n</b><code>{}</code>\nNotify: {}', 
    'pzd_with_args': '<b>🦊 PZD with args</b>',
    'status_created': '<b>🦊 Статус {} создан\n</b><code>{}</code>\nNotify: {}',
    'status_removed': '<b>🦊 Статус {} удален</b>',
    'no_status': '<b>🦊 Сейчас не стоит никакой статус</b>',
    'status_unset': '<b>🦊 Статус убран</b>',
    'available_statuses': '<b>🦊 Доступные статусы:</b>\n\n'}

    async def client_ready(self, client, db):
        self.db = db
        self.client = client
        self._me = await client.get_me(True)

    async def watcher(self, message):
        if not isinstance(message, types.Message):
            return

        if not self.db.get('Statuses', 'status', False):
            return

        if getattr(message.to_id, "user_id", None) == self._me.user_id:
            user = await utils.get_user(message)
            if user.is_self or user.bot or user.verified:
                return

            await utils.answer(message, self.db.get('Statuses', 'texts', {'': ''})[self.db.get('Statuses', 'status', '')])
            if not self.db.get('Statuses', 'notif', {'': False})[self.db.get('Statuses', 'status', '')]:
                await message.client.send_read_acknowledge(message.chat_id)

    async def statuscmd(self, message):
        args = utils.get_args_raw(message)
        if args not in self.db.get('Statuses', 'texts', {}):
            await tuils.answer(message, self.strings('status_not_found', message))
            await asyncio.sleep(3)
            await message.delete()
            return

        self.db.set('Statuses', 'status', args)
        await utils.answer(message, self.strings('status_set', message).format(utils.escape_html(self.db.get('Statuses', 'texts', {})[args]), str(self.db.get('Statuses', 'notif')[args])))

    async def newstatuscmd(self, message):
        """.newstatus <short_name> <notif|0/1> <text> - Новый статус"""
        args = utils.get_args_raw(message)
        args = args.split(' ', 2)
        if len(args) < 3:
            await utils.answer(message, self.strings('pzd_with_args', message))
            await asyncio.sleep(3)
            await message.delete()
            return

        if args[1] in ['1', 'true', 'yes', '+']:
            args[1] = True
        else:
            args[1] = False

        texts = self.db.get('Statuses', 'texts', {})
        texts[args[0]] = args[2]        
        self.db.set('Statuses', 'texts', texts)

        notif = self.db.get('Statuses', 'notif', {})
        notif[args[0]] = args[1]        
        self.db.set('Statuses', 'notif', notif)
        await utils.answer(message, self.strings('status_created', message).format(utils.escape_html(args[0]), utils.escape_html(args[2]), args[1]))

    async def delstatuscmd(self, message):
        """.delstatus <short_name> - Удалить статус"""
        args = utils.get_args_raw(message)
        if args not in self.db.get('Statuses', 'texts', {}):
            await utils.answer(message, self.strings('status_not_found', message))
            await asyncio.sleep(3)
            await message.delete()
            return

        texts = self.db.get('Statuses', 'texts', {})
        del texts[args]      
        self.db.set('Statuses', 'texts', texts)

        notif = self.db.get('Statuses', 'notif', {})
        del notif[args]       
        self.db.set('Statuses', 'notif', notif)
        await utils.answer(message, self.strings('status_removed', message).format(utils.escape_html(args)))

    async def unstatuscmd(self, message):
        """.unstatus - Убрать статус"""
        if not self.db.get('Statuses', 'status', False):
            await utils.answer(message, self.strings('no_status', message))
            await asyncio.sleep(3)
            await message.delete()
            return

        self.db.set('Statuses', 'status', False)
        await utils.answer(message, self.strings('status_unset', message))

    async def statusescmd(self, message):
        """.statuses - Показать доступные статусы"""
        res = self.strings('available_statuses', message)
        for short_name, status in self.db.get('Statuses', 'texts', {}).items():
            res += f"<b><u>{short_name}</u></b> | Notify: <b>{self.db.get('Statuses', 'notif', {})[short_name]}</b>\n{status}\n➖➖➖➖➖➖➖➖➖\n"

        await utils.answer(message, res)
