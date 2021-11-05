"""
    Copyright 2021 t.me/innocoffee
    Licensed under the Apache License, Version 2.0
    
    Author is not responsible for any consequencies caused by using this
    software or any of its parts. If you have any questions or wishes, feel
    free to contact Dan by sending pm to @innocoffee_alt.
"""

#<3 title: HomeWork
#<3 pic: https://img.icons8.com/fluency/48/000000/khan-academy.png
#<3 desc: Планнер домашних заданий поможет лучше учиться


from .. import loader, utils
import asyncio
from random import randint


@loader.tds
class HomeworkMod(loader.Module):
    """Simple Homework planner"""
    strings = {'name': 'HomeWork',
    'no_hometask': '<b>You haven\'t provided hometask</b>',
    'new_hometask': "<b>Hometask </b><code>#{}</code>:\n<pre>{}</pre>", 
    'not_found': '<b>🚫 Hometask not found</b',
    'removed': '<b>✅ Hometask removed</b>'}

    async def client_ready(self, client, db):
        self.db = db
        self.hw = self.db.get("HomeWork", "hw", {})

    async def hwcmd(self, message):
        """.hw <item> - New hometask"""

        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        if args == "" and not reply:
            await utils.answer(message, self.strings('no_hometask'))
            await asyncio.sleep(2)
            await message.delete()
            return

        if args == "" and reply:
            args = reply.text

        random_id = str(randint(10000, 99999))

        self.hw[random_id] = args

        self.db.set("HomeWork", "hw", self.hw)
        await utils.answer(message, self.strings('new_hometask', message).format(random_id, str(args)))

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
            await utils.answer(message, self.strings('not_found', message))
            await asyncio.sleep(2)
            await message.delete()
            return

        del self.hw[args]
        self.db.set("HomeWork", "hw", self.hw)
        await utils.answer(message, self.strings('removed', message))
        await asyncio.sleep(2)
        await message.delete()
