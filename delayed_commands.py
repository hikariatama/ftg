"""
    Copyright 2021 t.me/innocoffee
    Licensed under the Apache License, Version 2.0
    
    Author is not responsible for any consequencies caused by using this
    software or any of its parts. If you have any questions or wishes, feel
    free to contact Dan by sending pm to @innocoffee_alt.
"""


#<3 title: DelayedCommands
#<3 pic: https://img.icons8.com/fluency/48/000000/schedule-mail.png
#<3 desc: Отложенные команды, удаление вывода по прошествии времени.


from .. import loader, utils
import asyncio
import re

#requires: random json

@loader.tds
class DelayedMod(loader.Module):
    """Delayed commands"""
    strings = {'name': 'DelayedCommands',
    'no_such_command': '<b>No such command</b>',
    'output_will_be_removed_in': '{}\n\nThis output will be removed in {} sec(s)'}

    async def client_ready(self, client, db):
        self.db = db
        try:
            self.todolist = json.loads(self.db.get("ToDo", "todo"))
        except:
            self.todolist = {}

    @staticmethod
    def s2time(temp_time):
        seconds, minutes, hours, days, weeks, months = 0, 0, 0, 0, 0, 0
        
        try:            
            seconds = int(str(re.search('([0-9]+)s', temp_time).group(1)))
        except:
            pass

        try:
            minutes = int(str(re.search('([0-9]+)min', temp_time).group(1))) * 60
        except:
            pass

        try:
            hours = int(str(re.search('([0-9]+)h', temp_time).group(1))) * 60 * 60
        except:
            pass

        try:
            days = int(str(re.search('([0-9]+)d', temp_time).group(1))) * 60 * 60 * 24
        except:
            pass

        try:
            weeks = int(str(re.search('([0-9]+)w', temp_time).group(1))) * 60 * 60 * 24 * 7
        except:
            pass
        
        try:
            months = int(str(re.search('([0-9]+)m[^i]', temp_time).group(1))) * 60 * 60 * 24 * 31
        except:
            pass

        return round(seconds + minutes + hours + days + weeks + months)


    async def dcmd(self, message):
        """<time (1d 2min etc)> <cmd> - Delay command for specified time. Resets when module or ub are restarted"""
        args = utils.get_args_raw(message)

        command = args.split(' ', 1)[1]
        if command.startswith('.'):
            command = command[1:]

        if command.split()[0] not in self.allmodules.commands:
            await utils.answer(message, self.strings('no_such_command', message))
            await asyncio.sleep(3)
            await message.delete()
            return

        # print(args.split())

        reply = await message.get_reply_message()

        await message.delete()
        await asyncio.sleep(self.s2time(args.split()[0]))
        # await message.client.send_message('me', '.help')
        await self.allmodules.commands[command.split()[0]](await message.client.send_message(utils.get_chat_id(message), '.' + command, reply_to=reply))

    async def adcmd(self, message):
        """<time (1d 2min etc)> <cmd> - Execute command, and delete output after some time. WORKS NOT WITH ALL MODULES"""
        args = utils.get_args_raw(message)

        command = args.split(' ', 1)[1]
        if command.startswith('.'):
            command = command[1:]

        if command.split()[0] not in self.allmodules.commands:
            await utils.answer(message, self.strings('no_such_command', message))
            await asyncio.sleep(3)
            await message.delete()
            return

        # print(args.split())

        reply = await message.get_reply_message()

        await message.delete()
        # await message.client.send_message('me', '.help')
        msg = await message.client.send_message(utils.get_chat_id(message), '.' + command, reply_to=reply)
        # def _loc_edit(*args, **kwargs):
            # msg.text = kwargs.get("text", None) or args[0]
            # return msg._old_edit(*args, **kwargs)
        # msg._old_edit = msg.edit
        # msg.edit = _loc_edit
        await self.allmodules.commands[command.split()[0]](msg)
        # await asyncio.sleep(1)
        delay = self.s2time(args.split()[0])
        # await msg.edit(self.strings('output_will_be_removed_in', message).format(msg.text, str(delay)))
        # if delay > 10:
        await asyncio.sleep(delay)
        # else:
        #     for i in range(delay):
        #         await msg.edit('\n'.join(self.strings('output_will_be_removed_in', message).format(msg.text.split('\n')[:-2]), str(delay - i + 1)))
        #         await asyncio.sleep(1)
        await msg.delete()
