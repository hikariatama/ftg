"""
    Copyright 2021 t.me/innocoffee
    Licensed under the Apache License, Version 2.0
    
    Author is not responsible for any consequencies caused by using this
    software or any of its parts. If you have any questions or wishes, feel
    free to contact Dan by sending pm to @innocoffee_alt.
"""

# <3 title: InnoChat
# <3 pic: https://img.icons8.com/fluency/48/000000/manual.png
# <3 desc: Chat admin's toolkit

from .. import loader, utils
import telethon
import logging
import os
import time
import re
import json
import requests
import string


_client = None

old_utils = utils.answer
async def new_answer(message, text, *args, **kwargs):
    for inst in re.findall(r'tg://user\?id=([0-9]*)', text) or []:
        t = int(inst)
        try:
            if isinstance(await _client.get_input_entity(t), telethon.tl.types.InputPeerChannel):
                try:
                    username = (await _client.get_entity(t)).username
                except: username = ''
                text = text.replace(f'tg://user?id={t}', f'https://t.me/{username}' if username else '')
        except: pass

    return await old_utils(message, text, *args, **kwargs)

logger = logging.getLogger(__name__)


version = "v3.8beta"


@loader.tds
class InnoChatMod(loader.Module):
    """Chat admin's toolkit (must have)
Distributing without author's tag is strictly prohibited by license
This script is made by @innomods"""
    strings = {
        'name': 'InnoChat',

        'antisex_on': '🔞 <b>AntiSex On\nAction: {}</b>',
        'antisex_off': '🔞 <b>AntiSex Off</b>',
        'antisex': '🔞 <b><a href="tg://user?id={}">{}</a>, you\'re suspicious!\nAction: {}</b>',

        'atagall_on': '🐵 <b>AntiTagAll On\nAction: {}</b>',
        'atagall_off': '🐵 <b>AntiTagAll Off</b>',
        'tagall': '🐵 <b>Seems like <a href="tg://user?id={}">{}</a> used TagAll.\n👊 Action: I {}</b>',
        'args': '🦊 <b>Args are incorrect</b>',
        'atagall_action_set': '🐵 <b>AntiTagAll action set to "{}"</b>',

        'as_on': '🐻 <b>Arab Shield On\nAction: {}</b>',
        'as_off': '🐻 <b>Arab Shield Off</b>',
        'arabic_nickname': '🐻 <b>Seems like <a href="tg://user?id={}">{}</a> is Arab.\n👊 Action: I {}</b>',
        'arab_action_set': '🐻 <b>Arab shield action set to "{}"</b>',

        'antihelp_on': '🐺 <b>Anti Help On</b>',
        'antihelp_off': '🐺 <b>Anti Help Off</b>',

        'als_on': '🐼 <b>AntiLogspam On (Maximum {} per {} seconds)\nAction: {}</b>',
        'als_off': '🐼 <b>AntiLogspam Off</b>',
        'logspam': '🐼 <b>Seems like <a href="tg://user?id={}">{}</a> is LogSpamming.\n👊 Action: I {}</b>',
        'als_action_set': '🐼 <b>ALS action set to "{}"</b>',
        'als_range_set': '🐼 <b>Current limit of ALS is {} per {}</b>',

        'ar_on': '🐶 <b>AntiRaid On\nAction: {}</b>',
        'ar_off': '🐶 <b>AntiRaid Off</b>',
        'antiraid': '🐶 <b>AntiRaid is On. I {} <a href="tg://user?id={}">{}</a> in group {}</b>',

        'no_reason': 'Not specified',
        'warn': '👮‍♂️ <b><a href="tg://user?id={}">{}</a></b> got {}/{} warn\nReason: <b>{}</b>',
        'chat_not_in_db': '👮‍♂️ <b>This chat has no warns yet</b>',
        'no_warns': '👮‍♂️ <b><a href="tg://user?id={}">{}</a> has no warns yet</b>',
        'warns': '👮‍♂️ <b><a href="tg://user?id={}">{}</a> has {}/{} warns</b>\n    🏴󠁧󠁢󠁥󠁮󠁧󠁿 <i>{}</i>',
        'warns_adm': '👮‍♂️ <b>Warns in this chat</b>:\n',
        'dwarn': '👮‍♂️ <b>Removed last warn from <a href="tg://user?id={}">{}</a></b>',
        'clrwarns': '👮‍♂️ <b>Removed all warns from <a href="tg://user?id={}">{}</a></b>',
        'new_a': '👮‍♂️ <b>New action when warns limit is reached for this chat: "{}"</b>',
        'new_l': '👮‍♂️ <b>New warns limit for this chat: "{}"</b>',
        'warns_limit': '👮‍♂️ <b><a href="tg://user?id={}">{}</a> reached warns limit.\nAction: I {}</b>',

        'welcome': '👋 <b>Now I will greet people in this chat</b>',
        'chat_not_found': '👋 <b>I\'m not greeting people in this chat yet</b>',
        'unwelcome': '👋 <b>Not I will not greet people in this chat</b>',

        'chat404': '🦊 <b>I am not protecting this chat yet.</b>\n',
        'protections': '<b>🐻 AntiArab:</b> <code>.arab</code> <code>.arabaction</code>\n<b>🐼 AntiLogspam:</b> <code>.als</code> <code>.alsaction</code> <code>.alsset</code>\n<b>🐺 AntiHelp:</b> <code>.antihelp</code>\n<b>🐵 AntiTagAll:</b> <code>.atagall</code> <code>.atagallaction</code>\n<b>👋 Welcome: </b><code>.welcome</code> <code>.unwelcome</code>\n<b>🐶 AntiRaid:</b> <code>.araid</code>\n<b>🔞 AntiSex:</b> <code>.asex</code>\n<b>👾 Admin: </b><code>.ban</code> <code>.kick</code> <code>.mute</code> <code>.unban</code> <code>.unmute</code> <code>.setpref</code> <code>.delpref</code>\n<b>👮‍♂️ Warns:</b> <code>.warn</code> <code>.warns</code> <code>.dwarn</code> <code>.clrwarns</code> <code>.warnslimit</code> <code>.warnsaciton</code>',

        'prefix_set': '👾 <b><a href="tg://user?id={}">{}</a></b>\'s prefix is now <b>{}</b>',
        'prefix_removed': '👾 <b><a href="tg://user?id={}">{}</a> has no prefix now</b>',
        'not_admin': '👾 <b>I\'m not admin here, or don\'t have enough rights</b>',
        'mute': '👾 <b><a href="tg://user?id={}">{}</a> muted {}. Reason: {}</b>',
        'ban': '👾 <b><a href="tg://user?id={}">{}</a> banned {}. Reason: {}</b>',
        'kick': '👾 <b><a href="tg://user?id={}">{}</a> kicked. Reason: {}</b>',
        'unmuted': '👾 <b><a href="tg://user?id={}">{}</a> unmuted</b>',
        'unban': '👾 <b><a href="tg://user?id={}">{}</a> unbanned</b>',

        'defense': '🛡 <b>Shield for <a href="tg://user?id={}">{}</a> is now {}</b>',
        'no_defense': '🛡 <b>I don\'t protect any users in this chat right now</b>',
        'defense_list': '🛡 <b>Invulnerable users in current chat:</b>\n{}',

        'antichannel': '📯 <b>AntiChannel is now {} in this chat</b>'
    }

    async def client_ready(self, client, db):
        global _client
        self.db = db
        self.client = client
        _client = client
        self.me = str((await client.get_me()).id)
        self.chats = db.get('InnoChats', 'chats', {})
        self.warns = db.get('InnoChats', 'warns', {})
        try:
            self.cache = json.loads(open('als_cache.json', 'r').read())
        except:
            self.cache = {}

        self.correction = 1636106678


        async def deleted_handler(event):
            for msid in event.deleted_ids:
                # logger.debug(f'[AntiLogspam]: Looking for message {msid}')

                try:
                    cid = str(event.original_update.channel_id)
                except AttributeError:
                    # logger.debug(f'[AntiLogspam]: Got {event} from non-chat')
                    return

                if cid + '_' + str(msid) not in self.cache:
                    # logger.debug(f'[AntiLogspam]: Message not found, ignoring')
                    return

                try:
                    user = str(self.cache[cid + '_' + str(msid)][0])
                except:
                    # logger.exception(f'[AntiLogspam]: Unknown exception')
                    return

                # logger.debug(f'[AntiLogspam]: Found msg in cache from user {user}')

                if cid not in self.chats:
                    # logger.debug(f'[AntiLogspam]: Event from blacklisted channel')
                    return

                await self.check_user(cid, user, 'deleted')

        async def edited_handler(event):
            cid = str(utils.get_chat_id(event.message))
            user = str(event.message.from_id)
            await self.check_user(cid, user, 'edited', event)

        try:
            client.remove_event_handler(
                loader.logspam_edit_handler, telethon.events.MessageEdited())
        except:
            pass

        loader.logspam_edit_handler = edited_handler
        # try:
        #     client.remove_event_handler(
        #         loader.logspam_delete_handler, telethon.events.MessageDeleted())
        # except:
        #     pass
        # loader.logspam_delete_handler = deleted_handler

        await self.update_handlers()

    @loader.group_admin_ban_users
    async def kickcmd(self, message):
        """<reply | user> <reason | optional> - Kick user"""
        chat = await message.get_chat()
        if message.is_private:
            await message.delete()
            return

        if not chat.admin_rights and not chat.creator:
            return await new_answer(message, self.strings('not_admin', message))

        reply = await message.get_reply_message()
        args = utils.get_args_raw(message)
        user, reason = None, None

        try:
            if reply:
                user = await self.client.get_entity(reply.from_id)
                reason = args if args else self.strings('no_reason')
            else:
                uid = args.split(maxsplit=1)[0]
                try:
                    uid = int(uid)
                except:
                    pass
                user = await self.client.get_entity(uid)
                reason = args.split(maxsplit=1)[1] if len(
                    args.split(maxsplit=1)) > 1 else self.strings('no_reason')
        except:
            await new_answer(message, self.strings('args', message))
            return

        try:
            await self.client.kick_participant(utils.get_chat_id(message), user)
            await new_answer(message, self.strings('kick', message).format(user.id, user.first_name if getattr(user, 'first_name', None) is not None else user.title, reason))
        except telethon.errors.UserAdminInvalidError:
            await new_answer(message, self.strings('not_admin', message))
            return

    @loader.group_admin_ban_users
    async def bancmd(self, message):
        """<reply | user> <time | 0 for infinity> <reason | optional> - Ban user"""
        chat = await message.get_chat()
        if message.is_private:
            await message.delete()
            return

        reply = await message.get_reply_message()
        args = utils.get_args_raw(message)
        user, t, reason = None, 0, None

        try:
            if reply:
                user = await self.client.get_entity(reply.from_id)
                try:
                    t = int(args.split(maxsplit=1)[0])
                    reason = args.split(maxsplit=1)[1] if len(
                        args.split()) > 1 else self.strings('no_reason')
                except:
                    t = 0
                    reason = args if args else self.strings('no_reason')

            else:
                uid = args.split(maxsplit=1)[0]
                try:
                    uid = int(uid)
                except: pass
                user = await self.client.get_entity(uid)
                reason = args.split(maxsplit=1)[1] if len(
                    args.split(maxsplit=1)) > 1 else self.strings('no_reason')
        except:
            await new_answer(message, self.strings('args', message))
            return

        if not chat.admin_rights and not chat.creator:
            return await new_answer(message, self.strings('not_admin', message))

        try:
            await self.client.edit_permissions(chat, user, until_date=time.time() + t * 60, view_messages=False, send_messages=False, send_media=False, send_stickers=False, send_gifs=False, send_games=False, send_inline=False, send_polls=False, change_info=False, invite_users=False)
            await new_answer(message, self.strings('ban', message).format(user.id, user.first_name if getattr(user, 'first_name', None) is not None else user.title, f'for {t}min(-s)' if t != 0 else 'forever', reason))
        except telethon.errors.UserAdminInvalidError:
            await new_answer(message, self.strings('not_admin', message))
            return

    @loader.group_admin_ban_users
    async def mutecmd(self, message):
        """<reply | user> <time | 0 for infinity> <reason | optional> - Mute user"""
        chat = await message.get_chat()
        if message.is_private:
            await message.delete()
            return

        reply = await message.get_reply_message()
        args = utils.get_args_raw(message)
        user, t, reason = None, 0, None

        try:
            if reply:
                user = await self.client.get_entity(reply.from_id)
                try:
                    t = int(args.split(maxsplit=1)[0])
                    reason = args.split(maxsplit=1)[1] if len(
                        args.split()) > 1 else self.strings('no_reason')
                except:
                    t = 0
                    reason = args if args else self.strings('no_reason')

            else:
                uid = args.split(maxsplit=1)[0]
                try:
                    uid = int(uid)
                except: pass
                user = await self.client.get_entity(uid)
                reason = args.split(maxsplit=1)[1] if len(
                    args.split(maxsplit=1)) > 1 else self.strings('no_reason')
        except:
            await new_answer(message, self.strings('args', message))
            return

        if not chat.admin_rights and not chat.creator:
            return await new_answer(message, self.strings('not_admin', message))

        try:
            await self.client.edit_permissions(chat, user, until_date=time.time() + t * 60, send_messages=False)
            await new_answer(message, self.strings('mute', message).format(user.id, user.first_name if getattr(user, 'first_name', None) is not None else user.title, f'for {t}min(-s)' if t != 0 else 'forever', reason))
        except telethon.errors.UserAdminInvalidError:
            await new_answer(message, self.strings('not_admin', message))
            return

    @loader.group_admin_add_admins
    async def setprefcmd(self, message):
        """<reply | user> <prefix> - Set prefix w\\o admin rights"""
        chat = await message.get_chat()
        if message.is_private:
            await message.delete()
            return

        if not chat.admin_rights and not chat.creator:
            return await new_answer(message, self.strings('not_admin', message))

        reply = await message.get_reply_message()
        args = utils.get_args_raw(message)
        user, prefix = None, None

        try:
            if reply:
                user = await self.client.get_entity(reply.from_id)
                prefix = args if args else self.strings('no_reason')
            else:
                uid = args.split(maxsplit=1)[0]
                try:
                    uid = int(uid)
                except:
                    pass
                user = await self.client.get_entity(uid)
                prefix = args.split(maxsplit=1)[1] if len(
                    args.split(maxsplit=1)) > 1 else None
        except:
            await new_answer(message, self.strings('args', message))
            return

        try:
            await self.client(telethon.functions.channels.EditAdminRequest(message.peer_id, user, telethon.tl.types.ChatAdminRights(change_info=False, delete_messages=False, ban_users=False, pin_messages=False, add_admins=False, manage_call=False, anonymous=False, invite_users=True), prefix))
            await new_answer(message, self.strings('prefix_set', message).format(user.id, user.first_name if getattr(user, 'first_name', None) is not None else user.title, prefix))
        except telethon.errors.UserAdminInvalidError:
            await new_answer(message, self.strings('not_admin', message))
            return

    @loader.group_admin_add_admins
    async def delprefcmd(self, message):
        """<reply | user> - Remove prefix"""
        chat = await message.get_chat()
        if message.is_private:
            await message.delete()
            return

        if not chat.admin_rights and not chat.creator:
            return await new_answer(message, self.strings('not_admin', message))

        reply = await message.get_reply_message()
        args = utils.get_args_raw(message)
        user = None

        try:
            if reply:
                user = await self.client.get_entity(reply.from_id)
            else:
                try:
                    args = int(args)
                except: pass
                user = await self.client.get_entity(args)
        except:
            await new_answer(message, self.strings('args', message))
            return

        try:
            await self.client(telethon.functions.channels.EditAdminRequest(message.peer_id, user, telethon.tl.types.ChatAdminRights(change_info=False, delete_messages=False, ban_users=False, pin_messages=False, add_admins=False, manage_call=False, anonymous=False, invite_users=False), ''))
            await new_answer(message, self.strings('prefix_removed', message).format(user.id, user.first_name if getattr(user, 'first_name', None) is not None else user.title))
        except telethon.errors.UserAdminInvalidError:
            await new_answer(message, self.strings('not_admin', message))
            return

    @loader.group_admin_ban_users
    async def unmutecmd(self, message):
        """<reply | user> - Unmute user"""
        chat = await message.get_chat()
        if message.is_private:
            await message.delete()
            return

        if not chat.admin_rights and not chat.creator:
            return await new_answer(message, self.strings('not_admin', message))

        reply = await message.get_reply_message()
        args = utils.get_args_raw(message)
        user = None

        try:
            if reply:
                user = await self.client.get_entity(reply.from_id)
            else:
                try:
                    args = int(args)
                except: pass
                user = await self.client.get_entity(args)
        except:
            await new_answer(message, self.strings('args', message))
            return

        try:
            await self.client.edit_permissions(chat, user, until_date=0, send_messages=True)
            await new_answer(message, self.strings('unmuted', message).format(user.id, user.first_name if getattr(user, 'first_name', None) is not None else user.title))
        except telethon.errors.UserAdminInvalidError:
            await new_answer(message, self.strings('not_admin', message))
            return

    @loader.group_admin_ban_users
    async def unbancmd(self, message):
        """<reply | user> - Unban user"""
        chat = await message.get_chat()
        if message.is_private:
            await message.delete()
            return

        if not chat.admin_rights and not chat.creator:
            return await new_answer(message, self.strings('not_admin', message))

        reply = await message.get_reply_message()
        args = utils.get_args_raw(message)
        user = None

        try:
            if reply:
                user = await self.client.get_entity(reply.from_id)
            else:
                try:
                    args = int(args)
                except: pass
                user = await self.client.get_entity(args)
        except:
            await new_answer(message, self.strings('args', message))
            return

        try:
            await self.client.edit_permissions(chat, user, until_date=0, view_messages=True, send_messages=True, send_media=True, send_stickers=True, send_gifs=True, send_games=True, send_inline=True, send_polls=True, change_info=True, invite_users=True)
            await new_answer(message, self.strings('unban', message).format(user.id, user.first_name if getattr(user, 'first_name', None) is not None else user.title))
        except telethon.errors.UserAdminInvalidError:
            await new_answer(message, self.strings('not_admin', message))
            return

    @loader.group_owner
    async def asexcmd(self, message):
        """<mute | kick | ban | no to disable> - Toggle antisex"""
        

        chat = str(utils.get_chat_id(message))
        args = utils.get_args_raw(message)

        if chat not in self.chats:
            self.chats[chat] = {}

        if args in ['mute', 'ban', 'kick']:
            self.chats[chat]['antisex'] = args
            await new_answer(message, self.strings('antisex_on', message).format(args))
        else:
            if 'antisex' in self.chats[chat]:
                del self.chats[chat]['antisex']
            await new_answer(message, self.strings('antisex_off', message))

        self.db.set('InnoChats', 'chats', self.chats)

    @loader.group_owner
    async def araidcmd(self, message):
        """<mute | kick | ban | no to disable> - Toggle antiraid"""
        

        chat = str(utils.get_chat_id(message))
        args = utils.get_args_raw(message)

        if chat not in self.chats:
            self.chats[chat] = {}

        if args in ['mute', 'ban', 'kick']:
            self.chats[chat]['antiraid'] = args
            await new_answer(message, self.strings('ar_on', message).format(args))
        else:
            if 'antiraid' in self.chats[chat]:
                del self.chats[chat]['antiraid']
            await new_answer(message, self.strings('ar_off', message))

        self.db.set('InnoChats', 'chats', self.chats)

    @loader.group_owner
    async def atagallcmd(self, message):
        """Toggle AntiTagAll"""
        

        chat = str(utils.get_chat_id(message))
        if chat not in self.chats:
            self.chats[chat] = {}

        if 'antitagall' not in self.chats[chat]:
            self.chats[chat]['antitagall'] = 'mute'
            await new_answer(message, self.strings('atagall_on', message).format('mute'))
        else:
            del self.chats[chat]['antitagall']
            await new_answer(message, self.strings('atagall_off', message))

        self.db.set('InnoChats', 'chats', self.chats)

    @loader.group_owner
    async def atagallactioncmd(self, message):
        """<mute | ban | kick | warn | delmsg> - Set action raised on tagall"""
        

        args = utils.get_args_raw(message)
        chat = str(utils.get_chat_id(message))
        if args not in ['warn', 'ban', 'kick', 'mute', 'delmsg']:
            await new_answer(message, self.strings('args', message))
            return

        if chat not in self.chats:
            self.chats[chat] = {}

        self.chats[chat]['antitagall'] = args
        self.db.set('InnoChats', 'chats', self.chats)
        await new_answer(message, self.strings('atagall_action_set', message).format(args))

    @loader.group_owner
    async def antihelpcmd(self, message):
        """Toggle AntiHelp"""
        

        chat = str(utils.get_chat_id(message))
        if chat not in self.chats:
            self.chats[chat] = {}

        if 'antihelp' not in self.chats[chat]:
            self.chats[chat]['antihelp'] = True
            await new_answer(message, self.strings('antihelp_on', message).format('mute'))
        else:
            del self.chats[chat]['antihelp']
            await new_answer(message, self.strings('antihelp_off', message))

        self.db.set('InnoChats', 'chats', self.chats)

    @loader.group_owner
    async def arabcmd(self, message):
        """Toggle AntiArab"""
        

        chat = str(utils.get_chat_id(message))
        if chat not in self.chats:
            self.chats[chat] = {}

        if 'arabshield' not in self.chats[chat]:
            self.chats[chat]['arabshield'] = 'mute'
            await new_answer(message, self.strings('as_on', message).format('mute'))
        else:
            del self.chats[chat]['arabshield']
            await new_answer(message, self.strings('as_off', message))

        self.db.set('InnoChats', 'chats', self.chats)

    @loader.group_owner
    async def arabactioncmd(self, message):
        """<mute | ban | kick | warn | delmsg> - Set action raised on arab"""
        

        args = utils.get_args_raw(message)
        chat = str(utils.get_chat_id(message))
        if args not in ['warn', 'ban', 'kick', 'mute', 'delmsg']:
            await new_answer(message, self.strings('args', message))
            return

        if chat not in self.chats:
            self.chats[chat] = {}

        self.chats[chat]['arabshield'] = args
        self.db.set('InnoChats', 'chats', self.chats)
        await new_answer(message, self.strings('arab_action_set', message).format(args))

    @loader.group_owner
    async def alscmd(self, message):
        """Toggle LogSpam"""
        

        chat = str(utils.get_chat_id(message))
        if chat not in self.chats:
            self.chats[chat] = {}
        if 'als' not in self.chats[chat]:
            self.chats[chat]['als'] = {'settings': {
                'cooldown': 0,
                'detection_range': 5,
                'detection_interval': 15,
                'action': 'nothing'
            }
            }
            await new_answer(message, self.strings('als_on', message).format(self.chats[chat]['als']['settings']['detection_range'], self.chats[chat]['als']['settings']['detection_interval'], self.chats[chat]['als']['settings']['action']))
        else:
            del self.chats[chat]['als']
            await new_answer(message, self.strings('als_off', message))

        self.db.set('InnoChats', 'chats', self.chats)
        await self.update_handlers()

    @loader.group_owner
    async def alsactioncmd(self, message):
        """<mute | ban | kick | warn | delmsg | nothing> - Set action raised on limit"""
        

        args = utils.get_args_raw(message)
        chat = str(utils.get_chat_id(message))
        if args not in ['warn', 'ban', 'kick', 'mute', 'delmsg', 'nothing']:
            await new_answer(message, self.strings('args', message))
            return

        if chat not in self.chats:
            self.chats[chat] = {}

        if 'als' not in self.chats[chat]:
            self.chats[chat]['als'] = {}

        if 'settings' not in self.chats[chat]['als']:
            self.chats[chat]['als']['settings'] = {
                'cooldown': 0,
                'detection_range': 5,
                'detection_interval': 15,
                'action': 'nothing'
            }

        self.chats[chat]['als']['settings']['action'] = args
        self.db.set('InnoChats', 'chats', self.chats)
        await new_answer(message, self.strings('als_action_set', message).format(args))

    @loader.group_owner
    async def alssetcmd(self, message):
        """<limit> <time sample> - Set limit and time sample"""
        

        args = utils.get_args_raw(message)
        chat = str(utils.get_chat_id(message))
        if not args or len(args.split()) != 2:
            await new_answer(message, self.strings('args', message))
            return

        try:
            limit, time_sample = list(map(int, args.split()))
        except:
            await new_answer(message, self.strings('args', message))
            return

        if chat not in self.chats:
            self.chats[chat] = {}

        if 'als' not in self.chats[chat]:
            self.chats[chat]['als'] = {}

        if 'settings' not in self.chats[chat]['als']:
            self.chats[chat]['als']['settings'] = {
                'cooldown': 0,
                'detection_range': 5,
                'detection_interval': 15,
                'action': 'nothing'
            }

        self.chats[chat]['als']['settings']['detection_range'], self.chats[chat]['als']['settings']['detection_interval'] = limit, time_sample
        self.db.set('InnoChats', 'chats', self.chats)
        await new_answer(message, self.strings('als_range_set', message).format(limit, time_sample))

    @loader.group_owner
    async def update_handlers(self):
        # logger.info('[AntiLogspam]: Updating handlers')
        

        try:
            try:
                self.client.remove_event_handler(
                    loader.logspam_edit_handler, telethon.events.MessageEdited())
            except:
                pass
            self.client.add_event_handler(
                loader.logspam_edit_handler, telethon.events.MessageEdited(incoming=True))

            # try:
            #     self.client.remove_event_handler(
            #         loader.logspam_delete_handler, telethon.events.MessageDeleted())
            # except:
            #     pass
            # self.client.add_event_handler(
            #     loader.logspam_delete_handler, telethon.events.MessageDeleted())
        except:
            # logger.exception('[AntiLogspam]: Error when updating handlers')
            return

        # logger.info(f'[AntiLogspam]: Successfully started for {len(self.chats)} chats: {", ".join(self.chats)}')

    @loader.group_owner
    async def check_user(self, cid, user, event_type, event=None):
        if cid in self.chats and self.chats[cid] and 'defense' in self.chats[cid] and self.chats[cid]['defense'] and user in self.chats[cid]['defense']:
            return

        if user != self.me:
            if cid in self.chats:
                if 'als' in self.chats[cid]:
                    changes = False
                    if user not in self.chats[cid]['als']:
                        self.chats[cid]['als'][user] = []
                        changes = True

                    self.chats[cid]['als'][user].append(round(time.time()))

                    for u, timings in self.chats[cid]['als'].items():
                        if u == 'settings':
                            continue
                        loc_timings = timings.copy()
                        for timing in loc_timings:
                            if timing + self.chats[cid]['als']['settings']['detection_interval'] <= time.time():
                                self.chats[cid]['als'][u].remove(timing)
                                changes = True

                    if len(self.chats[cid]['als'][user]) >= self.chats[cid]['als']['settings']['detection_range']:
                        action = self.chats[cid]['als']['settings']['action']
                        if event_type != 'deleted':
                            try:
                                await event.message.delete()
                            except:
                                pass
                                # logger.exception(f'[AntiLogspam]: Error deleting logspam message')

                        if int(self.chats[cid]['als']['settings']['cooldown']) <= time.time():
                            try:
                                user_name = (await self.client.get_entity(int(user))).first_name
                            except:
                                user_name = "Brother"

                            await self.punish(int(cid), int(user), 'logspam', self.chats[cid]['als']['settings']['action'], user_name)

                            self.chats[cid]['als']['settings']['cooldown'] = round(
                                time.time()) + 15

                        del self.chats[cid]['als'][user]
                        changes = True

                    if changes:
                        self.db.set('InnoChats', 'chats', self.chats)
        else:
            logger.debug('[AntiLogspam]: Message from owner, ignoring...')

    @loader.group_owner
    async def protectscmd(self, message):
        """List available filters"""
        await new_answer(message, self.strings('protections', message))

    async def pchatscmd(self, message):
        """List protections"""
        

        res = f"<b><u>🦊 @innomods Chat Protection</u></b> <i>{version}</i>\n\n<i>🐼 - AntiLogspam\n🐺 - AntiHelp\n🐻 - AntiArab\n🐵 - AntiTagAll\n💋 - AntiSex\n🚪 - AntiRaid\n📯 - AntiChannel\n\n👋 - Welcome\n👮‍♂️ - Warns</i>\n\n🦊 <b><u>Chats:</u></b>\n"
        changes = False
        for chat, obj in self.chats.copy().items():
            try:
                chat_obj = await self.client.get_entity(int(chat))
                if getattr(chat_obj, 'title', False):
                    chat_name = chat_obj.title
                else:
                    chat_name = chat_obj.first_name
            except:
                del self.chats[chat]
                changes = True
                continue

            line = ""
            line += "🐼" if 'als' in obj else ""
            line += "🐺" if 'antihelp' in obj else ""
            line += "🐻" if 'arabshield' in obj else ""
            line += "🐵" if 'antitagall' in obj else ""
            line += "💋" if 'antisex' in obj else ""
            line += "🚪" if 'antiraid' in obj else ""
            line += "📯" if 'antichannel' in obj else ""
            line += "👋" if 'welcome' in obj else ""
            line += "👮‍♂️" if chat in self.warns else ""

            if not line:
                del self.chats[chat]
                changes = True
                continue

            res += "<code>    </code>◾️ " + chat_name + ": " + line + "\n"

        if changes:
            self.db.set('InnoChats', 'chats', self.chats)

        await new_answer(message, res)

    @loader.group_owner
    async def pchatcmd(self, message):
        """List protection for current chat"""
        

        cid = str(utils.get_chat_id(message))

        if cid not in self.chats or not self.chats[cid]:
            return await new_answer(message, self.strings('chat404', message))

        res = f"<b><u>🦊 @innomods Chat Protection</u></b> <i>{version}</i>\n"

        obj = self.chats[cid]

        line = ""
        line += "\n🐺 <b>AntiHelp.</b>" if 'antihelp' in obj else ""
        line += "\n🐵 <b>AntiTagAll.</b> Action: <b>{}</b>".format(
            obj['antitagall']) if 'antitagall' in obj else ""
        line += "\n🐻 <b>AntiArab.</b> Action: <b>{}</b>".format(
            obj['arabshield']) if 'arabshield' in obj else ""

        line += "\n🐼 <b>AntiLogspam.</b> Action: <b>{}</b> if <b>{}</b> per <b>{}s</b>".format(
            obj['als']['settings']['action'], obj['als']['settings']['detection_range'], obj['als']['settings']['detection_interval']) if 'als' in obj else ""
        line += "\n💋 <b>AntiSex</b> Action: <b>{}</b>".format(obj['antisex']) if 'antisex' in obj else ""
        line += "\n🚪 <b>AntiRaid</b> Action: <b>{} all joined</b>".format(obj['antiraid']) if 'antiraid' in obj else ""
        line += "\n📯 <b>AntiChannel.</b>" if 'antichannel' in obj else ""
        line += "\n👋 <b>Welcome.</b> \n<code>    </code>{}".format(
            obj['welcome'].replace('\n', '\n<code>    </code>')) if 'welcome' in obj else ""
        line += "\n👮‍♂️ <b>Warns.</b>" if cid in self.warns else ""

        res += line

        await new_answer(message, res)

    async def punish(self, cid, user, violation, action, user_name):
        

        self.warn = ('warn' in self.allmodules.commands)

        if action == "delmsg":
            await self.client.send_message(cid, self.strings(violation).format(user, user_name, 'deleted message'))
        elif action == "kick":
            await self.client.send_message(cid, self.strings(violation).format(user, user_name, 'kicked him'))
            await self.client.kick_participant(cid, user)
        elif action == "ban":
            await self.client.send_message(cid, self.strings(violation).format(user, user_name, 'banned him for 1 hour'))
            await self.client(telethon.tl.functions.channels.EditBannedRequest(cid, user, telethon.tl.types.ChatBannedRights(until_date=time.time() + 60 * 60, view_messages=True, send_messages=True, send_media=True, send_stickers=True, send_gifs=True, send_games=True, send_inline=True, embed_links=True)))
        elif action == "mute":
            await self.client.send_message(cid, self.strings(violation).format(user, user_name, 'muted him for 1 hour'))
            await self.client(telethon.tl.functions.channels.EditBannedRequest(cid, user, telethon.tl.types.ChatBannedRights(until_date=time.time() + 60 * 60, send_messages=True)))
        elif action == "warn":
            if not self.warn:
                await self.client.send_message(cid, self.strings(violation).format(user, user_name, 'should have warned him, but Warns is not installed'))
            else:
                warn_msg = await self.client.send_message(cid, f'.warn {user} {violation}')
                await self.allmodules.commands['warn'](warn_msg)
                await self.client.send_message(cid, self.strings(violation).format(user, user_name, 'warned him'))
        else:
            await self.client.send_message(cid, self.strings(violation).format(user, user_name, 'just chill 😶‍🌫️ '))

    def save_cache(self):
        open('als_cache.json', 'w').write(json.dumps(self.cache))


    @loader.group_admin_ban_users
    async def warncmd(self, message):
        """<reply | user_id | username> <reason | optional> - Warn user"""
        if message.is_private:
            await message.delete()
            return

        cid = str(utils.get_chat_id(message))
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        user = None
        if reply:
            user = await self.client.get_entity(reply.from_id)
            if args:
                reason = args
            else:
                reason = self.strings('no_reason')
        else:
            try:
                u = args.split(maxsplit=1)[0]
                try:
                    u = int(u)
                except:
                    pass

                user = await self.client.get_entity(u)
            except IndexError:
                return await new_answer(message, self.strings('args', message))

            try:
                reason = args.split(maxsplit=1)[1]
            except IndexError:
                reason = self.strings('no_reason')

        if cid not in self.warns:
            self.warns[cid] = {
                'a': 'mute',
                'l': 5,
                'w': {}
            }

        if user.id not in self.warns[cid]['w']:
            self.warns[cid]['w'][user.id] = []
        self.warns[cid]['w'][user.id].append(reason)

        if len(self.warns[cid]['w'][user.id]) >= self.warns[cid]['l']:
            action = self.warns[cid]['a']
            user_name = user.first_name if getattr(user, 'first_name', None) is not None else user.title
            user = user.id
            if action == "kick":
                await self.client.kick_participant(int(cid), int(user))
                await self.client.send_message(int(cid), self.strings('warns_limit').format(user, user_name, 'kicked him'))
            elif action == "ban":
                await self.client(telethon.tl.functions.channels.EditBannedRequest(int(cid), int(user), telethon.tl.types.ChatBannedRights(until_date=time.time() + 15 * 60, view_messages=True, send_messages=True, send_media=True, send_stickers=True, send_gifs=True, send_games=True, send_inline=True, embed_links=True)))
                await self.client.send_message(int(cid), self.strings('warns_limit').format(user, user_name, 'banned him for 15 mins'))
            elif action == "mute":
                await self.client(telethon.tl.functions.channels.EditBannedRequest(int(cid), int(user), telethon.tl.types.ChatBannedRights(until_date=time.time() + 15 * 60, send_messages=True)))
                await self.client.send_message(int(cid), self.strings('warns_limit').format(user, user_name, 'muted him for 15 mins'))

            await message.delete()
            self.warns[cid]['w'][user] = []
        else:
            await new_answer(message, self.strings('warn', message).format(user.id, user.first_name if getattr(user, 'first_name', None) is not None else user.title, len(self.warns[cid]['w'][user.id]), self.warns[cid]['l'], reason))
        self.db.set('InnoChats', 'warns', self.warns)

    @loader.unrestricted
    async def warnscmd(self, message):
        """<reply | user_id | username | optional> - Show warns in chat \\ of user"""
        if message.is_private:
            await message.delete()
            return

        cid = utils.get_chat_id(message)

        if str(cid) not in self.warns:
            return await new_answer(message, self.strings('chat_not_in_db', message))


        async def check_admin(user_id):
            return (await self.client.get_permissions(cid, user_id)).is_admin

        async def send_user_warns(usid):
            if str(cid) not in self.warns:
                await new_answer(message, self.strings('chat_not_in_db', message))
                return
            elif usid not in self.warns[str(cid)]['w'] or len(self.warns[str(cid)]['w'][usid]) == 0:
                user_obj = await self.client.get_entity(usid)
                await new_answer(message, self.strings('no_warns', message).format(user_obj.id, user_obj.first_name if getattr(user_obj, 'first_name', None) is not None else user_obj.title))
            else:
                user_obj = await self.client.get_entity(usid)
                await new_answer(message, self.strings('warns', message).format(user_obj.id, user_obj.first_name if getattr(user_obj, 'first_name', None) is not None else user_obj.title, len(self.warns[str(cid)]['w'][usid]), self.warns[str(cid)]['l'], '\n    🏴󠁧󠁢󠁥󠁮󠁧󠁿 '.join(self.warns[str(cid)]['w'][usid])))

        if not await check_admin(message.from_id):
            await send_user_warns(message.from_id)
        else:
            reply = await message.get_reply_message()
            args = utils.get_args_raw(message)
            if not reply and not args:
                res = self.strings('warns_adm', message) 
                for user, warns in self.warns[str(cid)]['w'].items():
                    user_obj = await self.client.get_entity(user)
                    res += "🐺 <b><a href=\"tg://user?id=" + str(user_obj.id) + "\">" + getattr(user_obj, 'first_name', '') + ' ' + (
                        user_obj.last_name if getattr(user_obj, 'last_name', '') is not None else '') + '</a></b>\n'
                    for warn in warns:
                        res += "<code>   </code>🏴󠁧󠁢󠁥󠁮󠁧󠁿 <i>" + warn + '</i>\n'

                await new_answer(message, res)
                return
            elif reply:
                await send_user_warns(reply.from_id)
            elif args:
                await send_user_warns(args)

    @loader.group_admin_ban_users
    async def dwarncmd(self, message):
        """<reply | user_id | username> - Remove last warn"""
        if message.is_private:
            await message.delete()
            return

        cid = str(utils.get_chat_id(message))
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        user = None
        if reply:
            user = await self.client.get_entity(reply.from_id)
        else:
            try:
                args = int(args)
            except: pass

            try:
                user = await self.client.get_entity(args)
            except IndexError:
                return await new_answer(message, self.strings('args', message))

        if cid not in self.warns:
            return await new_answer(message, self.strings('chat_not_in_db', message))

        if user.id not in self.warns[cid]['w']:
            return await new_answer(message, self.strings('no_warns', user.id, user.first_name if getattr(user, 'first_name', None) is not None else user.title))

        del self.warns[cid]['w'][user.id][-1]
        await new_answer(message, self.strings('dwarn', message).format(user.id, user.first_name if getattr(user, 'first_name', None) is not None else user.title))
        self.db.set('InnoChats', 'warns', self.warns)

    @loader.group_admin_ban_users
    async def clrwarnscmd(self, message):
        """<reply | user_id | username> - Remove all warns from user"""
        if message.is_private:
            await message.delete()
            return

        cid = str(utils.get_chat_id(message))
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        user = None
        if reply:
            user = await self.client.get_entity(reply.from_id)
        else:
            try:
                args = int(args)
            except: pass
        
            try:
                user = await self.client.get_entity(args)
            except IndexError:
                return await new_answer(message, self.strings('args', message))

        if cid not in self.warns:
            return await new_answer(message, self.strings('chat_not_in_db', message))

        if user.id not in self.warns[cid]['w']:
            return await new_answer(message, self.strings('no_warns').format(user.id, user.first_name if getattr(user, 'first_name', None) is not None else user.title))

        del self.warns[cid]['w'][user.id]
        await new_answer(message, self.strings('clrwarns', message).format(user.id, user.first_name if getattr(user, 'first_name', None) is not None else user.title))
        self.db.set('InnoChats', 'warns', self.warns)

    @loader.group_admin_ban_users
    async def warnsactioncmd(self, message):
        """<mute | kick | ban> - Set action when limit is reached"""
        if message.is_private:
            await message.delete()
            return

        args = utils.get_args_raw(message)
        if not args or args not in ['mute', 'kick', 'ban']:
            return await new_answer(message, self.strings('args', message))

        cid = utils.get_chat_id(message)

        if str(cid) not in self.warns:
            self.warns[str(cid)] = {
                'a': 'mute',
                'l': 5,
                'w': {}
            }

        self.warns[str(cid)]['a'] = args
        await new_answer(message, self.strings('new_a', message).format(args))

    @loader.group_admin_ban_users
    async def warnslimitcmd(self, message):
        """<limit:int> - Set warns limit"""
        if message.is_private:
            await message.delete()
            return

        args = utils.get_args_raw(message)
        try:
            args = int(args)
        except:
            return await new_answer(message, self.strings('args', message))

        cid = utils.get_chat_id(message)

        if str(cid) not in self.warns:
            self.warns[str(cid)] = {
                'a': 'mute',
                'l': 5,
                'w': {}
            }

        self.warns[str(cid)]['l'] = args
        await new_answer(message, self.strings('new_l', message).format(args))

    @loader.group_owner
    async def welcomecmd(self, message):
        """<text> - Change welcome text"""
        cid = str(utils.get_chat_id(message))
        args = utils.get_args_raw(message)
        if cid not in self.chats:
            self.chats[cid] = {}

        self.chats[cid]['welcome'] = args
        self.db.set('InnoChats', 'chats', self.chats)
        await new_answer(message, self.strings('welcome', message))

    @loader.group_owner
    async def unwelcomecmd(self, message):
        """Disable greeting"""
        cid = str(utils.get_chat_id(message))
        args = utils.get_args_raw(message)

        if cid not in self.chats:
            self.chats[cid] = {}

        if 'welcome' not in self.chats[cid]:
            await new_answer(message, self.strings('chat_not_found', message))
            return

        del self.chats[cid]['welcome']
        self.db.set('InnoChats', 'chats', self.chats)
        await new_answer(message, self.strings('unwelcome', message))

    @loader.group_owner
    async def antichannelcmd(self, message):
        """Toggle messages removal from channels"""
        cid = str(utils.get_chat_id(message))
        if cid not in self.chats:
            self.chats[cid] = {}

        if 'antichannel' not in self.chats[cid]:
            self.chats[cid]['antichannel'] = True
            await new_answer(message, self.strings('antichannel').format('on'))
        else:
            del self.chats[cid]['antichannel']
            await new_answer(message, self.strings('antichannel').format('off'))

    @loader.group_owner
    async def defensecmd(self, message):
        """<user | reply> - Toggle user invulnerability"""
        if message.is_private:
            await message.delete()
            return

        cid = str(utils.get_chat_id(message))
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        user = None
        if reply:
            user = await self.client.get_entity(reply.from_id)
        else:
            try:
                args = int(args)
            except: pass

            try:
                user = await self.client.get_entity(args)
            except IndexError:
                return await new_answer(message, self.strings('args', message))

        if cid not in self.chats:
            self.chats[cid] = {}

        if 'defense' not in self.chats[cid]:
            self.chats[cid]['defense'] = []

        if user.id not in self.chats[cid]['defense']:
            self.chats[cid]['defense'].append(user.id)
            await new_answer(message, self.strings('defense', message).format(user.id, user.first_name if getattr(user, 'first_name', None) is not None else user.title if getattr(user, 'first_name', None) is not None else user.title, 'on'))
        else:
            self.chats[cid]['defense'].remove(user.id)
            await new_answer(message, self.strings('defense', message).format(user.id, user.first_name if getattr(user, 'first_name', None) is not None else user.title if getattr(user, 'first_name', None) is not None else user.title, 'off'))

        self.db.set('InnoChats', 'chats', self.chats)

    @loader.group_owner
    async def defenselistcmd(self, message):
        chat = str(utils.get_chat_id(message))
        if chat not in self.chats or not self.chats[chat] or 'defense' not in self.chats[chat] or not self.chats[chat]['defense']:
            return await new_answer(message, self.strings('no_defense', message))

        res = ""
        defense = self.chats[chat]['defense']
        for user in defense.copy():
            try:
                u = await self.client.get_entity(user)
            except:
                self.chats[chat]['defense'].remove(user)
                continue

            tit = u.first_name if getattr(u, 'first_name', None) is not None else u.title
            res += f"  🇻🇦 <a href=\"tg://user?id={u.id}\">{tit}{(' ' + u.last_name) if getattr(u, 'last_name', None) is not None else ''}</a>\n"

        return await new_answer(message, self.strings('defense_list').format(res))


    async def watcher(self, message):
        

        try:
            cid = str(utils.get_chat_id(message))

            if cid not in self.chats or not self.chats[cid]:
                return

            user = message.from_id if getattr(message, 'from_id', None) is not None else 0
            if user < 0:
                user = int(str(user)[4:])
            # logger.info(user)
            if 'defense' in self.chats[cid] and user in self.chats[cid]['defense']:
                return

            try:
                if (await self.client.get_permissions(int(cid), message.from_id)).is_admin: return
            except: pass

            # Anti Raid:

            if 'antiraid' in self.chats[cid]:
                if getattr(message, "user_joined", False) or getattr(message, "user_added", False):
                    user = await message.get_user()
                    chat = await message.get_chat()
                    user_name = getattr(user, 'first_name', '') + ' ' + (
                        user.last_name if getattr(user, 'last_name', '') is not None else '')
                    action = self.chats[cid]['antiraid']
                    if action == "kick":
                        await self.client.send_message('me', self.strings('antiraid').format('kicked', user, user_name, chat.title))
                        await self.client.kick_participant(int(cid), user)
                    elif action == "ban":
                        await self.client.send_message('me', self.strings('antiraid').format('banned', user, user_name, chat.title))
                        await self.client(telethon.tl.functions.channels.EditBannedRequest(int(cid), user, telethon.tl.types.ChatBannedRights(until_date=0, view_messages=True, send_messages=True, send_media=True, send_stickers=True, send_gifs=True, send_games=True, send_inline=True, embed_links=True)))
                    elif action == "mute":
                        await self.client.send_message('me', self.strings('antiraid').format('muted', user, user_name, chat.title))
                        await self.client(telethon.tl.functions.channels.EditBannedRequest(int(cid), user, telethon.tl.types.ChatBannedRights(until_date=0, send_messages=True)))

                    return

            if 'antisex' in self.chats[cid]:
                if getattr(message, "user_joined", False) or getattr(message, "user_added", False):
                    user = await message.get_user()
                    chat = await message.get_chat()
                    user_name = getattr(user, 'first_name', '') + ' ' + (
                        user.last_name if getattr(user, 'last_name', '') is not None else '')
                    replacing = {
                        "3Z8z": "З",
                        "HN7hn": "Н",
                        "A5a": "А",
                        "K4k": "К",
                        "O0o": "О",
                        "Mm": "М",
                        "CSc": "С"
                    }

                    for key, value in replacing.items():
                        for letter in list(key):
                            user_name = user_name.replace(letter, value)

                    # logger.info(user_name)

                    if 'ЗНАКОМС' in user_name:
                        # user_name = ''.join([_ for _ in user_name if _ in string.hexdigits])
                        action = self.chats[cid]['antisex']
                        if action == "kick":
                            await self.client.send_message(chat, self.strings('antisex').format(user.id, user_name, 'kicked'))
                            await self.client.kick_participant(int(cid), user)
                        elif action == "ban":
                            await self.client.send_message(chat, self.strings('antisex').format(user.id, user_name, 'banned'))
                            await self.client(telethon.tl.functions.channels.EditBannedRequest(int(cid), user, telethon.tl.types.ChatBannedRights(until_date=0, view_messages=True, send_messages=True, send_media=True, send_stickers=True, send_gifs=True, send_games=True, send_inline=True, embed_links=True)))
                        elif action == "mute":
                            await self.client.send_message(chat, self.strings('antisex').format(user.id, user_name, 'muted'))
                            await self.client(telethon.tl.functions.channels.EditBannedRequest(int(cid), user, telethon.tl.types.ChatBannedRights(until_date=0, send_messages=True)))

                        return

            if 'welcome' in self.chats[cid]:
                if getattr(message, "user_joined", False) or getattr(message, "user_added", False):
                    user = await message.get_user()
                    chat = await message.get_chat()
                    await self.client.send_message(int(cid), self.chats[cid]['welcome'].replace('{user}', user.first_name if getattr(user, 'first_name', None) is not None else user.title).replace('{chat}', chat.title).replace('{mention}', '<a href="tg://user?id=' + str(user.id) + '">' + user.first_name if getattr(user, 'first_name', None) is not None else user.title + '</a>'), reply_to=message.action_message.id)
                    
                    return

            user = message.from_id or None

            # AntiChannel:

            if 'antichannel' in self.chats[cid]:
                if user < 0:
                    await message.delete()
                    return

            # AntiLogSpam:

            if 'als' in self.chats[cid]:
                if user is not None and str(user) != self.me:
                    msid = message.id
                    self.cache[cid + "_" + str(msid)] = (user,
                                                         round(time.time()) - self.correction)
                    for key, info in self.cache.copy().items():
                        if time.time() - info[1] - self.correction >= 86400:
                            del self.cache[key]
                    self.save_cache()

            violation = None

            user_obj = await self.client.get_entity(int(user))
            user_name = getattr(user_obj, 'first_name', '') + ' ' + (
                user_obj.last_name if getattr(user_obj, 'last_name', '') is not None else '')

            # AntiTagAll:

            if 'antitagall' in self.chats[cid]:
                if message.text.count('tg://user?id=') >= 5:
                    violation = 'tagall'
                    action = self.chats[cid]['antitagall']

            # AntiHelp:
            if 'antihelp' in self.chats[cid]:
                search = message.text
                if '@' in search:
                    search = search[:search.find('@')]
                    tagged = True
                else:
                    tagged = False

                blocked_commands = ['help', 'dlmod', 'loadmod', 'lm', 'sq', 'q', 'ping']

                if len(search.split()) > 0 and search.split()[0][1:] in blocked_commands:
                    await message.delete()
                    # if tagged:
                    #     try:
                    #         await self.allmodules.commands['warn'](await self.client.send_message(message.peer_id, f'.warn {user} calling help of another member'))
                    #     except:
                    #         pass
                    #     await asyncio.sleep(2)
                    #     async for msg in self.client.iter_messages(int(cid), offset_id=message.id, reverse=True):
                    #         if msg is telethon.tl.types.Message and msg.reply_to.reply_to_msg_id == message.id:
                    #             await self.client.delete_messages(int(cid), [msg])

            # Arab Shield:
            if 'arabshield' in self.chats[cid]:
                to_check = getattr(message, 'message', '') + \
                    getattr(message, 'caption', '') + user_name
                if len(re.findall('[\u4e00-\u9fff]+', to_check)) != 0 or len(re.findall('[\u0621-\u064A]+', to_check)) != 0:
                    violation = 'arabic_nickname'
                    action = self.chats[cid]['arabshield']

            if violation is None:
                return

            await self.punish(int(cid), int(user), violation, action, user_name)

            try:
                await message.delete()
            except:
                pass

        except Exception as e:
            logger.exception(e)
            pass
