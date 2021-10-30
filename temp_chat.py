"""
    Copyright 2021 t.me/innocoffee
    Licensed under the Apache License, Version 2.0
    
    Author is not responsible for any consequencies caused by using this
    software or any of its parts. If you have any questions or wishes, feel
    free to contact Dan by sending pm to @innocoffee_alt.
"""

#<3 title: TempChat
#<3 pic: https://img.icons8.com/fluency/48/000000/pause-squared.png
#<3 desc: Создает временный чат для, например, совместной работы над проектом

from .. import loader, utils
import asyncio
import json
import re
import datetime
import time
import telethon

# requires: json


@loader.tds
class TempChatMod(loader.Module):
    """Creates temprorary chats to avoid trashcans in TG."""
    strings = {"name": "TempChat"}

    @staticmethod
    def s2time(temp_time):
        seconds, minutes, hours, days, weeks, months = 0, 0, 0, 0, 0, 0

        try:
            seconds = int(str(re.search('([0-9]+)s', temp_time).group(1)))
        except:
            pass

        try:
            minutes = int(
                str(re.search('([0-9]+)min', temp_time).group(1))) * 60
        except:
            pass

        try:
            hours = int(
                str(re.search('([0-9]+)h', temp_time).group(1))) * 60 * 60
        except:
            pass

        try:
            days = int(
                str(re.search('([0-9]+)d', temp_time).group(1))) * 60 * 60 * 24
        except:
            pass

        try:
            weeks = int(
                str(re.search('([0-9]+)w', temp_time).group(1))) * 60 * 60 * 24 * 7
        except:
            pass

        try:
            months = int(
                str(re.search('([0-9]+)m[^i]', temp_time).group(1))) * 60 * 60 * 24 * 31
        except:
            pass

        return round(time.time() + seconds + minutes + hours + days + weeks + months)

    async def chats_handler_async(self):
        while True:
            # await self.client.send_message('me', 'testing')
            for chat, info in self.chats.items():
                if int(info[0]) <= time.time():
                    try:
                        await self.client.send_message(int(chat), '<b>🚫 This chat is being removed...</b>')
                        async for user in self.client.iter_participants(int(chat), limit=50):
                            await self.client.kick_participant(int(chat), user.id)
                        await self.client.delete_dialog(int(chat))
                    except:
                        try:
                            await self.client.send_message(int(chat), '<b>An error occured while deleting this temp chat. Remove it manually. @innocoffee</b>')
                        except:
                            pass

                    del self.chats[chat]
                    self.db.set("TempChat", "chats", self.chats)
                    break
            await asyncio.sleep(3)

    async def client_ready(self, client, db):
        self.db = db
        self.chats = self.db.get("TempChat", "chats", {})
        self.client = client
        asyncio.ensure_future(self.chats_handler_async())

    async def tmpchatcmd(self, message):
        """.tmpchat <time> <title> - Create new temp chat
You can specified time only in this format: 30s, 30min, 1h, 1d, 1w, 1m
30 secods, 30 minutes, 1 hour, 1 day, 1 week, 1 month"""
        await utils.answer(message, '<b>Reading args</b>')
        args = utils.get_args_raw(message)
        if args == "":
            await utils.answer(message, '<b>PZD with args. Refer to </b><code>.help TempChat</code>')
            await asyncio.sleep(3)
            await message.delete()
            return

        if len(args.split()) < 2:
            await utils.answer(message, '<b>PZD with args: </b><code>.help TempChat</code>')
            await asyncio.sleep(3)
            await message.delete()
            return

        temp_time = args.split()[0]
        tit = args.split(' ', 1)[1].strip()

        until = self.s2time(temp_time)
        if until == round(time.time()):
            await utils.answer(message, '<b>PZD with args: </b><code>.help TempChat</code>')
            await asyncio.sleep(3)
            await message.delete()
            return

        res = await message.client(telethon.functions.messages.CreateChatRequest(users=['kanekiguard_tests_bot'], title=tit))
        await message.delete()
        cid = res.chats[0].id

        await message.client.send_message(cid, f'<b>⚠️ This chat</b> (<code>{cid}</code>)<b> is temporary and will be removed {datetime.datetime.utcfromtimestamp(until).strftime("%d.%m.%Y %H:%M:%S")}.</b>')
        self.chats[str(cid)] = [until, tit]
        self.db.set("TempChat", "chats", self.chats)

        await self.start_handler()

    async def tmpchatscmd(self, message):
        """.tmpchats - List temp chats"""
        res = "<b>= Temporary Chats =</b>\n<s>==================</s>\n"
        for chat, info in self.chats.items():
            res += f'<b>{info[1]}</b> (<code>{chat}</code>)<b>: {datetime.datetime.utcfromtimestamp(info[0]).strftime("%d.%m.%Y %H:%M:%S")}.</b>\n'
        res += "<s>==================</s>"

        await utils.answer(message, res)

    async def tmpcancelcmd(self, message):
        """.tmpcancel <chat-id | optional> - Disable deleting chat by id, or current chat if unspecified."""
        args = utils.get_args_raw(message)
        if args not in self.chats:
            args = str(utils.get_chat_id(message))

        if args not in self.chats:
            await utils.answer(message, '<b>Chat not found in temp db</b>')
            await asyncio.sleep(3)
            await message.delete()
            return

        await utils.answer(message, f'<b>Chat </b><code>{self.chats[args][1]}</code><b> will now live forever!</b>')
        del self.chats[args]
        self.db.set("TempChat", "chats", json.dumps(self.chats))

    async def tmpctimecmd(self, message):
        """.tmpctime <chat_id> <new_time>"""
        args = utils.get_args_raw(message)
        if args == "":
            await utils.answer(message, '<b>PZD with args: </b><code>.help TempChat</code>')
            await asyncio.sleep(3)
            await message.delete()
            return

        args = args.split()
        if len(args) == 0:
            await utils.answer(message, '<b>PZD with args: </b><code>.help TempChat</code>')
            await asyncio.sleep(3)
            await message.delete()
            return

        if len(args) >= 2:
            chat = args[0]
            new_time = self.s2time(args[1])
        else:
            chat = str(utils.get_chat_id(message))
            new_time = self.s2time(args[0])

        if chat not in list(self.chats.keys()):
            await utils.answer(message, '<b>No such chat</b>')
            await asyncio.sleep(3)
            await message.delete()
            return

        self.chats[chat][0] = new_time
        self.db.set('TempChat', 'chats', self.chats)
