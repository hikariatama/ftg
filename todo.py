"""
    Copyright 2021 t.me/innocoffee
    Licensed under the Apache License, Version 2.0
    
    Author is not responsible for any consequencies caused by using this
    software or any of its parts. If you have any questions or wishes, feel
    free to contact Dan by sending pm to @innocoffee_alt.
"""


from .. import loader, utils
import asyncio
from random import randint
import json

# requires: random json


@loader.tds
class TodoMod(loader.Module):
    """ToDo List"""
    strings = {'name': 'ToDo'}

    async def client_ready(self, client, db):
        self.db = db
        try:
            self.todolist = json.loads(self.db.get("ToDo", "todo"))
        except:
            self.todolist = {}

        self.imp_levels = ['🌌 Watchlist', '💻 Proging',
                           '⌚️ Work', '🎒 Family', '🚫 Private']

    async def tdcmd(self, message):
        """.td <importance:int> <item> - Добавить задачу в todo"""

        args = utils.get_args_raw(message)
        try:
            importance = int(args.split()[0])
            task = args.split(' ', 1)[1]
        except:
            importance = 0
            task = args

        try:
            if task != '':
                importance = int(task)
            else:
                importance = 0
            reply = await message.get_reply_message()
            if reply:
                task = reply.text
        except:
            pass

        if importance >= len(self.imp_levels):
            importance = 0

        random_id = str(randint(10000, 99999))

        self.todolist[random_id] = [task, importance]

        self.db.set("ToDo", "todo", json.dumps(self.todolist))
        await utils.answer(message, "<b>Задача </b><code>#" + random_id + "</code>:\n<pre>" + str(task) + '</pre>\n' + self.imp_levels[importance])

    async def tdlcmd(self, message):
        """.tdl - Показать активные задачи"""
        res = "<b>#ToDo:</b>\n"
        items = {}
        for i in range(len(self.imp_levels)):
            items[len(self.imp_levels) - i - 1] = []

        for item_id, item in self.todolist.items():
            items[item[1]].append(
                " <code>.utd " + item_id + "</code>: <code>" + item[0] + "</code>")

        for importance, strings in items.items():
            if len(strings) == 0:
                continue
            res += "\n -{ " + self.imp_levels[importance][2:] + " }-\n"
            res += self.imp_levels[importance][0] + \
                ('\n' + self.imp_levels[importance][0]).join(strings) + "\n"

        await utils.answer(message, res)

    async def utdcmd(self, message):
        """.utd <id> - Удалить задачу из todo"""
        args = utils.get_args_raw(message)
        if args.startswith('#'):
            args = args[1:]

        if args not in self.todolist:
            await utils.answer(message, '<b>🚫 Задача не найдена</b')
            await asyncio.sleep(2)
            await message.delete()
            return

        del self.todolist[args]
        self.db.set("ToDo", "todo", json.dumps(self.todolist))
        await utils.answer(message, '<b>✅ Задача удалена</b>')
        await asyncio.sleep(2)
        await message.delete()
