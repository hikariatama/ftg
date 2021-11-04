"""
    Copyright 2021 t.me/innocoffee
    Licensed under the Apache License, Version 2.0
    
    Author is not responsible for any consequencies caused by using this
    software or any of its parts. If you have any questions or wishes, feel
    free to contact Dan by sending pm to @innocoffee_alt.
"""

#<3 title: AntiLogspam
#<3 pic: https://img.icons8.com/fluency/48/000000/flash-bang.png
#<3 desc: Банит челов, которые засоряют логи

from .. import loader, utils
import telethon
import json
import logging
import os
import time

logger = logging.getLogger(__name__)

"""

.eval content = open('friendly-telegram/main.py', 'r').read().replace('dispatcher = CommandDispatcher(modules, db, is_bot, __debug__ and arguments.self_test)\n            if', 'dispatcher = CommandDispatcher(modules, db, is_bot, __debug__ and arguments.self_test)\n            loader.dispatcher = dispatcher\n            if')
if 'loader.dispatcher' not in content: return 'ERROR!'
open('friendly-telegram/main.py', 'w').write(content)
return 'OK'


"""

@loader.tds
class AntiLogspamMod(loader.Module):
    """Банит челов, которые срут в логах. Для старта нужно выполнить команду"""
    strings = {
        'name': 'AntiLogspam', 
        'als_on': '🦊 <b>AntiLogspam On (Maximum {} edits per {} seconds)</b>',
        'als_off': '🦊 <b>AntiLogspam Off</b>',
        'dont_spam': '🦊 <b>Seems like the message from <a href="tg://user?id={}">{}</a> contains LogSpam. Action: I {}</b>'
    }
    
    def __init__(self):
        self.config = loader.ModuleConfig("detection_range", 10, lambda: "Number of edits per time range", 
                                        "detection_interval", 30, lambda: "Detection interval in seconds",
                                        "action", 'delmsg', lambda: "Action on limit: delmsg/mute/kick/ban", 
                                        "cooldown", 15, lambda: "Cooldown of warning message in chat")

    async def client_ready(self, client, db):
        self.db = db
        self.client = client
        me = (await client.get_me()).id
        
        os.popen('mkdir innoconfig').read()
        try:
            self.chats = json.loads(open('innoconfig/AntiLogspam.json', 'r').read())
        except:
            self.chats = {}
            open('innoconfig/AntiLogspam.json', 'w').write('{}')
            logger.debug('[AntiLogspam]: Starting with clear config')

        main_py = open('friendly-telegram/main.py', 'r').read()
        if 'loader.dispatcher' not in main_py:
            logger.debug('[AntiLogspam]: Installing update for main.py... Backup saved as main.py.backup')
            os.popen('cp friendly-telegram/main.py friendly-telegram/main.py.backup').read()
            content = main_py.replace('dispatcher = CommandDispatcher(modules, db, is_bot, __debug__ and arguments.self_test)\n            if', 'dispatcher = CommandDispatcher(modules, db, is_bot, __debug__ and arguments.self_test)\n            loader.dispatcher = dispatcher\n            if')
            if 'loader.dispatcher' not in content:
                logger.error('[AntiLogspam]: Installation failed.')
                return

            open('friendly-telegram/main.py', 'w').write(content)
            logger.debug('[AntiLogspam]: Installed successfully')

        original_handler = loader.dispatcher.handle_command

        async def _dispatcher_wrapper(event):
            cid = str(utils.get_chat_id(event.message))
            user = str(event.message.from_id)
            if user != me:
                try:
                    user_name = (await client.get_entity(int(user))).first_name
                except:
                    user_name = "Brother"

                if cid in self.chats:
                    changes = False
                    if user not in self.chats[cid]:
                        self.chats[cid][user] = []
                        changes = True

                    self.chats[cid][user].append(round(time.time()))

                    for u, timings in self.chats[cid].items():
                        if u == 'cooldown': continue
                        loc_timings = timings.copy()
                        for timing in loc_timings:
                            if timing + self.config['detection_interval'] <= time.time():
                                self.chats[cid][u].remove(timing)
                                changes = True

                    if len(self.chats[cid][user]) >= self.config['detection_range']:
                        action = self.config['action']
                        await event.message.delete()
                        if int(self.chats[cid]['cooldown']) <= time.time():
                            if action == "delmsg":
                                await client.send_message(int(cid), self.strings('dont_spam').format(user, user_name, 'deleted message'))
                            elif action == "mute":
                                await client(telethon.tl.functions.channels.EditBannedRequest(cid, user, telethon.tl.types.ChatBannedRights(until_date=time.time() + int(n), send_messages=True)))
                                await client.send_message(int(cid), self.strings('dont_spam').format(user, user_name, 'muted him'))
                            elif action == "kick":
                                await client.kick_participant(cid, user)
                                await client.send_message(int(cid), self.strings('dont_spam').format(user, user_name, 'kicked him'))
                            elif action == "ban":
                                await client(telethon.tl.functions.channels.EditBannedRequest(cid, user, telethon.tl.types.ChatBannedRights(until_date=None, view_messages=True, send_messages=True, send_media=True, send_stickers=True, send_gifs=True, send_games=True, send_inline=True, embed_links=True)))
                                await client.send_message(int(cid), self.strings('dont_spam').format(user, user_name, 'banned him'))

                            self.chats[cid]['cooldown'] = round(time.time()) + self.config['cooldown']

                        self.chats[cid][user] = []
                        changes = True

                    if changes:
                        open('innoconfig/AntiLogspam.json', 'w').write(json.dumps(self.chats))
            else:
                logger.debug('[AntiLogspam]: Message from owner, ignoring...')

            return await original_handler(event)

        logger.debug('[AntiLogspam]: Updating handlers')
        client.remove_event_handler(loader.dispatcher.handle_command, telethon.events.MessageEdited())
        loader.dispatcher.handle_command = _dispatcher_wrapper
        client.add_event_handler(loader.dispatcher.handle_command, telethon.events.MessageEdited())
        logger.debug('[AntiLogspam]: Successfully started')

    async def antilogspamcmd(self, message):
        """.antilogspam - Toggle LogSpam protection in current chat"""
        chat = str(utils.get_chat_id(message))
        if chat not in self.chats:
            self.chats[chat] = {'cooldown': 0}
            await utils.answer(message, self.strings('als_on', message).format(self.config['detection_range'], self.config['detection_interval']))
        else:
            del self.chats[chat]
            await utils.answer(message, self.strings('als_off', message))

        open('innoconfig/AntiLogspam.json', 'w').write(json.dumps(self.chats))
