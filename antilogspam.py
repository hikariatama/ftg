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
from subprocess import DEVNULL, STDOUT, check_call

logger = logging.getLogger(__name__)


@loader.tds
class AntiLogspamMod(loader.Module):
    """Банит челов, которые срут в логах"""
    strings = {
        'name': 'AntiLogspam', 
        'als_on': '🦊 <b>AntiLogspam On (Maximum {} per {} seconds)\nAction: {}</b>',
        'als_off': '🦊 <b>AntiLogspam Off</b>',
        'dont_spam': '🦊 <b>Seems like <a href="tg://user?id={}">{}</a> is LogSpamming. Action: I {}</b>', 
        'args': '🦊 <b>Args are incorrect</b>',
        'action_set': '🦊 <b>Action set to "{}"</b>',
        'range_set': '🦊 <b>Current limit is {} per {}</b>'
    }

    async def check_user(self, cid, user, event_type, event=None):
        if user != self.me:
            if cid in self.chats:
                changes = False
                if user not in self.chats[cid]:
                    self.chats[cid][user] = []
                    changes = True

                self.chats[cid][user].append(round(time.time()))

                for u, timings in self.chats[cid].items():
                    if u == 'settings': continue
                    loc_timings = timings.copy()
                    for timing in loc_timings:
                        if timing + self.chats[cid]['settings']['detection_interval'] <= time.time():
                            self.chats[cid][u].remove(timing)
                            changes = True

                if len(self.chats[cid][user]) >= self.chats[cid]['settings']['detection_range']:
                    action = self.chats[cid]['settings']['action']
                    if event_type != 'deleted':
                        try:
                            await event.message.delete()
                        except:
                            logger.exception(f'[AntiLogspam]: Error deleting logspam message')

                    if int(self.chats[cid]['settings']['cooldown']) <= time.time():
                        try:
                            user_name = (await self.client.get_entity(int(user))).first_name
                        except:
                            user_name = "Brother"

                        self.warn = ('warn' in self.allmodules.commands)

                        if action == "delmsg" and event_type != 'deleted':
                            await self.client.send_message(int(cid), self.strings('dont_spam').format(user, user_name, 'deleted message'))
                        elif action == "kick":
                            await self.client.kick_participant(int(cid), int(user))
                            await self.client.send_message(int(cid), self.strings('dont_spam').format(user, user_name, 'kicked him'))
                        elif action == "ban":
                            await self.client(telethon.tl.functions.channels.EditBannedRequest(int(cid), int(user), telethon.tl.types.ChatBannedRights(until_date=time.time() + 15 * 60, view_messages=True, send_messages=True, send_media=True, send_stickers=True, send_gifs=True, send_games=True, send_inline=True, embed_links=True)))
                            await self.client.send_message(int(cid), self.strings('dont_spam').format(user, user_name, 'banned him for 15 mins'))
                        elif action == "mute" or not self.warn and event_type == 'deleted':
                            await self.client(telethon.tl.functions.channels.EditBannedRequest(int(cid), int(user), telethon.tl.types.ChatBannedRights(until_date=time.time() + 15 * 60, send_messages=True)))
                            await self.client.send_message(int(cid), self.strings('dont_spam').format(user, user_name, 'muted him for 15 mins'))
                        elif action == "warn" or event_type == 'deleted':
                            if not self.warn:
                                await self.client.send_message(int(cid), self.strings('dont_spam').format(user, user_name, 'should have warned him, but Warns is not installed'))
                            else:
                                warn_msg = await self.client.send_message(int(cid), f'.warn {user} logspam')
                                await self.allmodules.commands['warn'](warn_msg)
                                await self.client.send_message(int(cid), self.strings('dont_spam').format(user, user_name, 'warned him'))


                        self.chats[cid]['settings']['cooldown'] = round(time.time()) + 15

                    self.chats[cid][user] = []
                    changes = True

                if changes:
                    open('innoconfig/AntiLogspam.json', 'w').write(json.dumps(self.chats))
        else:
            logger.debug('[AntiLogspam]: Message from owner, ignoring...')

    async def client_ready(self, client, db):
        self.db = db
        self.client = client
        self.me = str((await client.get_me()).id)
        try:
            check_call(['mkdir', 'innoconfig'], stdout=DEVNULL, stderr=STDOUT)
        except:
            pass
        try:
            self.chats = json.loads(open('innoconfig/AntiLogspam.json', 'r').read())
        except:
            self.chats = {}
            open('innoconfig/AntiLogspam.json', 'w').write('{}')
            logger.warning('[AntiLogspam]: Starting with clear config')

        try:
            self.cache = json.loads(open('innoconfig/AntiLogspam_cache.json', 'r').read())
        except:
            self.cache = {}
            open('innoconfig/AntiLogspam_cache.json', 'w').write('{}')
            logger.info('[AntiLogspam]: Starting with clear cache')

        self.correction = 1636106678

        async def deleted_handler(event):
            #logger.info(f'[AntiLogspam]: {event}')
            for msid in event.deleted_ids:
                logger.debug(f'[AntiLogspam]: Looking for message {msid}')

                try:
                    cid = str(event.original_update.channel_id)
                except AttributeError:
                    logger.debug(f'[AntiLogspam]: Got {event} from non-chat')
                    return

                if cid + '_' + str(msid) not in self.cache:
                    logger.debug(f'[AntiLogspam]: Message not found, ignoring')
                    return

                try:
                    user = str(self.cache[cid + '_' + str(msid)][0])
                except:
                    logger.exception(f'[AntiLogspam]: Unknown exception')
                    return

                logger.debug(f'[AntiLogspam]: Found msg in cache from user {user}')

                if cid not in self.chats:
                    logger.debug(f'[AntiLogspam]: Event from blacklisted channel')
                    return


                await self.check_user(cid, user, 'deleted')


        async def edited_handler(event):
            cid = str(utils.get_chat_id(event.message))
            user = str(event.message.from_id)
            await self.check_user(cid, user, 'edited', event)

        try:
            client.remove_event_handler(loader.logspam_edit_handler, telethon.events.MessageEdited())
        except:
            pass

        loader.logspam_edit_handler = edited_handler
        try:
            client.remove_event_handler(loader.logspam_delete_handler, telethon.events.MessageDeleted())
        except:
            pass
        loader.logspam_delete_handler = deleted_handler

        await self.update_handlers()


    async def update_handlers(self):
        # logger.info('[AntiLogspam]: Updating handlers')
        try:
            try:
                self.client.remove_event_handler(loader.logspam_edit_handler, telethon.events.MessageEdited())
            except:
                pass
            self.client.add_event_handler(loader.logspam_edit_handler, telethon.events.MessageEdited(incoming=True))

            try:
                self.client.remove_event_handler(loader.logspam_delete_handler, telethon.events.MessageDeleted())
            except:
                pass
            self.client.add_event_handler(loader.logspam_delete_handler, telethon.events.MessageDeleted())
        except:
            logger.exception('[AntiLogspam]: Error when updating handlers')
            return

        logger.info(f'[AntiLogspam]: Successfully started for {len(self.chats)} chats: {", ".join(self.chats)}')

    async def antilogspamcmd(self, message):
        """.antilogspam - Toggle LogSpam protection in current chat"""
        chat = str(utils.get_chat_id(message))
        if chat not in self.chats:
            self.chats[chat] = {'settings': {
                    'cooldown': 0,
                    'detection_range': 5, 
                    'detection_interval': 15,
                    'action': 'delmsg'
                }
            }
            await utils.answer(message, self.strings('als_on', message).format(self.chats[chat]['settings']['detection_range'], self.chats[chat]['settings']['detection_interval'], self.chats[chat]['settings']['action']))
        else:
            del self.chats[chat]
            await utils.answer(message, self.strings('als_off', message))

        await self.update_handlers()

        open('innoconfig/AntiLogspam.json', 'w').write(json.dumps(self.chats))

    async def alsactioncmd(self, message):
        """.alsaction <mute | ban | kick | warn | delmsg> - Set action raised on limit for current chat"""
        args = utils.get_args_raw(message)
        chat = str(utils.get_chat_id(message))
        if args not in ['warn', 'ban', 'kick', 'mute', 'delmsg']:
            await utils.answer(message, self.strings('args', message))
            return

        if chat not in self.chats:
            self.chats[chat] = {'settings': {
                    'cooldown': 0,
                    'detection_range': 5, 
                    'detection_interval': 15,
                    'action': 'delmsg'
                }
            }

        if 'settings' not in self.chats[chat]:
            self.chats[chat]['settings'] = {
                    'cooldown': 0,
                    'detection_range': 5, 
                    'detection_interval': 15,
                    'action': 'delmsg'
                }

        self.chats[chat]['settings']['action'] = args
        open('innoconfig/AntiLogspam.json', 'w').write(json.dumps(self.chats))
        await utils.answer(message, self.strings('action_set', message).format(args))


    async def alssetcmd(self, message):
        """.alsset <limit> <range (time sample)> - Set limit and time sample for current chat"""
        args = utils.get_args_raw(message)
        chat = str(utils.get_chat_id(message))
        if not args or len(args.split()) != 2:
            await utils.answer(message, self.strings('args', message))
            return

        try:
            limit, time_sample = list(map(int, args))
        except:
            await utils.answer(message, self.strings('args', message))
            return

        if chat not in self.chats:
            self.chats[chat] = {'settings': {
                    'cooldown': 0,
                    'detection_range': 5, 
                    'detection_interval': 15,
                    'action': 'delmsg'
                }
            }

        if 'settings' not in self.chats[chat]:
            self.chats[chat]['settings'] = {
                    'cooldown': 0,
                    'detection_range': 5, 
                    'detection_interval': 15,
                    'action': 'delmsg'
                }

        self.chats[chat]['settings']['detection_range'], self.chats[chat]['settings']['detection_interval'] = limit, time_sample
        open('innoconfig/AntiLogspam.json', 'w').write(json.dumps(self.chats))
        await utils.answer(message, self.strings('range_set', message).format(limit, time_sample))


    def save_cache(self):
        open('innoconfig/AntiLogspam_cache.json', 'w').write(json.dumps(self.cache))

    async def watcher(self, message):
        cid = str(utils.get_chat_id(message))
        if str(message.from_id) == self.me:
            return

        if cid not in self.chats:
            return

        msid = message.id

        logger.debug(f'[AntiLogspam]: Adding message {msid} to cache (from user: {message.from_id})')

        self.cache[cid + "_" + str(msid)] = (message.from_id, round(time.time()) - self.correction)

        for key, info in self.cache.copy().items():
            if time.time() - info[1] - self.correction >= 86400:
                del self.cache[key]

        self.save_cache()
