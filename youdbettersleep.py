"""
    Copyright 2021 t.me/hikariakami
    Licensed under the Apache License, Version 2.0
    
    Author is not responsible for any consequencies caused by using this
    software or any of its parts. If you have any questions or wishes, feel
    free to contact Dan by sending pm to @hikari_alt.
"""

# <3 title: YouDBetterSleep
# <3 pic: https://img.icons8.com/fluency/48/000000/sleep.png
# <3 desc: Не дает тебе писать, чтобы ты мог поспать

from .. import loader, utils
import re
import time

def s2time(temp_time):
    seconds, minutes, hours = 0, 0, 0

    try:
        seconds = int(str(re.search('([0-9]+)s', temp_time).group(1)))
    except: pass

    try:
        minutes = int(str(re.search('([0-9]+)m', temp_time).group(1))) * 60
    except: pass

    try:
        hours = int(str(re.search('([0-9]+)h', temp_time).group(1))) * 60 * 60
    except: pass

    return round(seconds + minutes + hours)




@loader.tds
class YouDBetterSleepMod(loader.Module):
    strings = {
        "name": "YouDBetterSleep",
        "no_time": "👾 <b>You can't sleep forever, specify <time> argument</b>",
        "awake": "👾 <b>Good morning. Shit, I'm still alive...</b>",
        "asleep": "👾 <b>Good night. Now I can't write messages for {}</b>",
        "disabled": "👾 <b>I can't write messages, because my userbot wants me to sleep</b>"
    }

    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        self.until = 0
        self.asleep = db.get(__name__, 'asleep', False)

    @loader.sudo
    async def sleepcmd(self, message):
        """<time> - Sleep for time"""
        args = utils.get_args_raw(message)
        t = s2time(args)
        if not args or t == 0:
            self.asleep = False
            self.until = 0
            self.db.set(__name__, 'asleep', False)
            await utils.answer(message, self.strings('awake'))
        else:
            self.asleep = True
            self.until = t + time.time()
            self.db.set(__name__, 'asleep', True)
            self.db.set(__name__, 'until', t)
            await utils.answer(message, self.strings('asleep').format(args))

    async def watcher(self, message):
        try:
            if not self.asleep: return
            if message.text == ".sleep": return
            if self.until <= time.time():
                self.until = 0
                self.asleep = False
                await self.client.send_message('@userbot_notifies_bot', self.strings('awake'))
                return

            if message.mentioned:
                await self.client.send_read_acknowledge(message.peer_id, message, clear_mentions=True)
                await utils.answer(message, self.strings('disabled'))
            if not message.out: return

            await utils.answer(message, self.strings('disabled'))
        except: pass
