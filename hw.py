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
class HomeworkMod(loader.Module):
    """Simple Homework planner"""
    strings = {'name': 'HomeWork'}

    async def client_ready(self, client, db):
        self.db = db
        try:
            self.hw = json.loads(self.db.get("HomeWork", "hw"))
        except:
            self.hw = {}

    async def hwcmd(self, message):
        """.hw <item> - New hometask"""

        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        if args == "" and not reply:
            await utils.answer(message, '<b>You haven\'t provided hometask</b>')
            await asyncio.sleep(2)
            await message.delete()
            return

        if args == "" and reply:
            args = reply.text

        random_id = str(randint(10000, 99999))

        self.hw[random_id] = args

        self.db.set("HomeWork", "hw", json.dumps(self.hw))
        await utils.answer(message, "<b>Hometask </b><code>#" + random_id + "</code>:\n<pre>" + str(args) + '</pre>')

    async def hwlcmd(self, message):
        """.hwl - List of hometasks"""
        res = "<b>#HW:</b>\n\n"
        for item_id, item in self.hw.items():
            res += "🔸 <code>.uhw " + item_id + "</code>: <code>" + item + "</code>\n"
        await utils.answer(message, res)

    async def uhwcmd(self, message):
        """.uhw <id> - Remove hometask"""
        args = utils.get_args_raw(message)
        if args.startswith('#'):
            args = args[1:]

        if args not in self.hw:
            await utils.answer(message, '<b>🚫 Hometask not found</b')
            await asyncio.sleep(2)
            await message.delete()
            return

        del self.hw[args]
        self.db.set("HomeWork", "hw", json.dumps(self.hw))
        await utils.answer(message, '<b>✅ Hometask removed</b>')
        await asyncio.sleep(2)
        await message.delete()
