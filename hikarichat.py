# disable_onload_docs

"""
    Copyright 2021 t.me/hikariatama
    Licensed under the Apache License, Version 2.0

    Author is not responsible for any consequencies caused by using this
    software or any of its parts. If you have any questions or wishes, feel
    free to contact Dan by sending pm to @hikari_alt.
"""

# <3 title: HikariChat
# <3 pic: https://img.icons8.com/fluency/48/000000/manual.png
# <3 desc: Chat admin's toolkit

import re
import io
import abc
import time
import json
import copy
import imghdr
import logging
import asyncio
import aiohttp
import telethon
import functools
import traceback
from telethon.tl.types import *
from .. import loader, utils, main
from telethon.tl.types import User
from telethon.errors import UserAdminInvalidError
from telethon.tl.functions.channels import EditBannedRequest

from contextlib import suppress

logger = logging.getLogger(__name__)

__version__ = (7, 2, 19)
version = f"v{__version__[0]}.{__version__[1]}b{__version__[2]}"
ver = f'<u>HikariChat {version}</u>'

FLOOD_TIMEOUT = .5
FLOOD_TRESHOLD = 3
API_UPDATE_DELAY = 20


def get_link(user: User or Channel) -> str:
    return (
        f'tg://user?id={user.id}'
        if isinstance(user, User)
        else (
            f"tg://resolve?domain={user.username}"
            if getattr(user, 'username', None)
            else ""
        )
    )


def get_first_name(user: User or Channel) -> str:
    return user.first_name if isinstance(user, User) else user.title


def get_full_name(user: User or Channel) -> str:
    return (
        user.title
        if isinstance(user, Channel)
        else (
            user.first_name + ' ' + (
                user.last_name if getattr(user, 'last_name', False) else ''
            )
        )
    )


async def get_message_link(message: Message, chat: Chat or Channel = None) -> str:
    if not chat:
        chat = await message.get_chat()

    return (
        f"https://t.me/{chat.username}/{message.id}"
        if getattr(chat, 'username', False)
        else
        f"https://t.me/c/{chat.id}/{message.id}"
    )    


class HikariAPI:
    def __init__(self):
        pass

    async def init(self,
                 client: "telethon.client.telegramclient.TelegramClient",
                 db: "friendly-telegram.database.frontend.Database",
                 module: "friendly-telegram.modules.python.PythonMod"):
        """Entry point"""
        self.client = client
        self.db = db
        self.token = db.get('HikariChat', 'apitoken', False)
        self.module = module

        await self.assert_token()

        token_valid = await self.validate_token()
        if not token_valid:
            await self.client.send_message('@userbot_notifies_bot', utils.escape_html(f'<b>You are using an unregistered copy of HikariChat. Please, consider removing it with </b><code>{self.module.prefix}unloadmod HikariChat</code><b>, otherwise you will see flood messages</b>'))
            self.token = False

    async def assert_token(self) -> None:
        if not self.token:
            async with self.client.conversation('@innoapi_auth_' + 'bot') as conv:
                m = await conv.send_message("@get+innochat+token")
                res = await conv.get_response()
                await conv.mark_read()
                self.token = res.raw_text
                await m.delete()
                await res.delete()
                self.db.set('HikariChat', 'apitoken', self.token)

        
    async def validate_token(self) -> None:
        if not self.token:
            return False

        answ = await self.get('ping')
        if not answ['success']:
            return False

        return True

    async def request(self, method, *args, **kwargs) -> dict:
        if not self.token:
            return {'success': False}
        kwargs['headers'] = {
            'Authorization': f'Bearer {self.token}'
        }
        args = (f"https://api.hikariatama.ru/{args[0]}",)
        if 'json' in kwargs:
            kwargs['json']['version'] = __version__
        else:
            kwargs['json'] = {'version': __version__}
        async with aiohttp.ClientSession() as session:
            async with session.request(method, *args, **kwargs) as resp:
                r = await resp.text()
                try:
                    r = json.loads(r)
                except Exception:
                    await self.report_error(r)
                    return {'success': False}

                if 'success' not in r:
                    await self.report_error(json.dumps(r, indent=4))
                    return {'success': False}

                return r

    @asyncio.coroutine
    async def get(self, *args, **kwargs) -> dict:
        return await self.request('GET', *args, **kwargs)

    @asyncio.coroutine
    async def post(self, *args, **kwargs) -> dict:
        return await self.request('POST', *args, **kwargs)

    @asyncio.coroutine
    async def delete(self, *args, **kwargs) -> dict:
        return await self.request('DELETE', *args, **kwargs)

    @asyncio.coroutine
    async def report_error(self, error: str) -> dict:
        error = str(error)
        error = re.sub(r'^.*File .*in wrapped.*$', '', error)
        async with aiohttp.ClientSession() as session:
            async with session.request('POST', "https://api.hikariatama.ru/report_error", json={
                    'error': error[:2048]
                }, headers={
                    'Authorization': f'Bearer {self.token}'
                }) as resp:
                return





api = HikariAPI()

class HikariChatMod(loader.Module):
    """Bear with us while docstrings are loading"""
    __metaclass__ = abc.ABCMeta

    strings = {
        'name': 'HikariChat',

        'args': '🦊 <b>Args are incorrect</b>',
        'no_reason': 'Not specified',

        'antitagall_on': '🐵 <b>AntiTagAll is now on in this chat\nAction: {}</b>',
        'antitagall_off': '🐵 <b>AntiTagAll is now off in this chat</b>',

        'antiarab_on': '🐻 <b>AntiArab is now on in this chat\nAction: {}</b>',
        'antiarab_off': '🐻 <b>AntiArab is now off in this chat</b>',

        'antihelp_on': '🐺 <b>Anti Help On</b>',
        'antihelp_off': '🐺 <b>Anti Help Off</b>',

        'antiraid_on': '🐶 <b>AntiRaid is now on in this chat\nAction: {}</b>',
        'antiraid_off': '🐶 <b>AntiRaid is now off in this chat</b>',
        'antiraid': '🐶 <b>AntiRaid is On. I {} <a href="{}">{}</a> in group {}</b>',

        'antichannel_on': '📯 <b>AntiChannel is now on in this chat</b>',
        'antichannel_off': '📯 <b>AntiChannel is now off in this chat</b>',

        'report_on': '📣 <b>Report is now on in this chat</b>',
        'report_off': '📣 <b>Report is now off in this chat</b>',

        'antiflood_on': '⏱ <b>AntiFlood is now on in this chat\nAction: {}</b>',
        'antiflood_off': '⏱ <b>AntiFlood is now off in this chat</b>',

        'antispoiler_on': '🪙 <b>AntiSpoiler is now on in this chat</b>',
        'antispoiler_off': '🪙 <b>AntiSpoiler is now off in this chat</b>',

        'antinsfw_on': '🍓 <b>AntiNSFW is now on in this chat\nAction: {}</b>',
        'antinsfw_off': '🍓 <b>AntiNSFW is now off in this chat</b>',

        'arabic_nickname': '🐻 <b>Seems like <a href="{}">{}</a> is Arab.\n👊 Action: I {}</b>',
        'nsfw_content': '🍓 <b>Seems like <a href="{}">{}</a> sent NSFW content.\n👊 Action: I {}</b>',
        'flood': '⏱ <b>Seems like <a href="{}">{}</a> is flooding.\n👊 Action: I {}</b>',
        'tagall': '🐵 <b>Seems like <a href="{}">{}</a> used TagAll.\n👊 Action: I {}</b>',
        'sex_datings': '🔞 <b><a href="{}">{}</a> is suspicious 🧐\n👊 Action: I {}</b>',

        'fwarn': '👮‍♂️💼 <b><a href="{}">{}</a></b> got {}/{} federative warn\nReason: <b>{}</b>',
        'no_fed_warns': '👮‍♂️ <b>This federation has no warns yet</b>',
        'no_warns': '👮‍♂️ <b><a href="{}">{}</a> has no warns yet</b>',
        'warns': '👮‍♂️ <b><a href="{}">{}</a> has {}/{} warns</b>\n    🏴󠁧󠁢󠁥󠁮󠁧󠁿 <i>{}</i>',
        'warns_adm_fed': '👮‍♂️ <b>Warns in this federation</b>:\n',
        'dwarn_fed': '👮‍♂️ <b>Removed last federative warn from <a href="tg://user?id={}">{}</a></b>',
        'clrwarns_fed': '👮‍♂️ <b>Removed all federative warns from <a href="tg://user?id={}">{}</a></b>',
        'warns_limit': '👮‍♂️ <b><a href="{}">{}</a> reached warns limit.\nAction: I {}</b>',

        'welcome': '👋 <b>Now I will greet people in this chat</b>\n{}',
        'unwelcome': '👋 <b>Not I will not greet people in this chat</b>',

        'chat404': '🦊 <b>I am not protecting this chat yet.</b>\n',
        'protections': """<b>🐻 AntiArab:</b> <code>.antiarab</code>
<b>🐺 AntiHelp:</b> <code>.antihelp</code>
<b>🐵 AntiTagAll:</b> <code>.antitagall</code>
<b>👋 Welcome: </b><code>.welcome</code>
<b>🐶 AntiRaid:</b> <code>.antiraid</code>
<b>📯 AntiChannel:</b> <code>.antichannel</code>
<b>🪙 AntiSpoiler:</b> <code>.antispoiler</code>
<b>🍓 AntiNSFW:</b> <code>.antinsfw</code>
<b>⏱ AntiFlood:</b> <code>.antiflood</code>
<b>👾 Admin: </b><code>.ban</code> <code>.kick</code> <code>.mute</code>
<code>.unban</code> <code>.unmute</code>
<b>👮‍♂️ Warns:</b> <code>.warn</code> <code>.warns</code>
<code>.dwarn</code> <code>.clrwarns</code>
<b>💼 Federations:</b> <code>.fadd</code> <code>.frm</code> <code>.newfed</code>
<code>.namefed</code> <code>.fban</code> <code>.rmfed</code> <code>.feds</code>
<code>.fpromote</code> <code>.fdemote</code> <code>.fdef</code> <code>.fdeflist</code>
<b>🗒 Notes:</b> <code>.fsave</code> <code>.fstop</code> <code>.fnotes</code>""",

        'not_admin': '👾 <b>I\'m not admin here, or don\'t have enough rights</b>',
        'mute': '👾 <b><a href="{}">{}</a> muted {}. Reason: {}</b>',
        'ban': '👾 <b><a href="{}">{}</a> banned {}. Reason: {}</b>',
        'kick': '👾 <b><a href="{}">{}</a> kicked. Reason: {}</b>',
        'unmuted': '👾 <b><a href="{}">{}</a> unmuted</b>',
        'unban': '👾 <b><a href="{}">{}</a> unbanned</b>',

        'defense': '🛡 <b>Shield for <a href="{}">{}</a> is now {}</b>',
        'no_defense': '🛡 <b>Federative defense list is empty</b>',
        'defense_list': '🛡 <b>Federative defense list:</b>\n{}',

        'fadded': '💼 <b>Current chat added to federation "{}"</b>',
        'newfed': '💼 <b>Created federation "{}"</b>',
        'rmfed': '💼 <b>Removed federation "{}"</b>',
        'fed404': '💼 <b>Federation not found</b>',
        'frem': '💼 <b>Current chat removed from federation "{}"</b>',
        'f404': '💼 <b>Current chat is not in federation "{}"</b>',
        'fexists': '💼 <b>Current chat is already in federation "{}"</b>',
        'fedexists': '💼 <b>Federation exists</b>',
        'joinfed': '💼 <b>Federation joined</b>',
        'namedfed': '💼 <b>Federation renamed to {}</b>',
        'nofed': '💼 <b>Current chat is not in any federation</b>',
        'fban': '💼 <b><a href="{}">{}</a> banned in federation {}\nReason: {}</b>',
        'feds_header': '💼 <b>Federations:</b>\n\n',
        'fed': '''
💼 <b>Federation "{}" info:</b>
🔰 <b>Chats:</b>
<b>{}</b>
🔰 <b>Admins:</b>
<b>{}</b>
🔰 <b>Warns: {}</b>''',
        'no_fed': '💼 <b>This chat is not in any federation</b>',
        'fpromoted': '💼 <b><a href="{}">{}</a> promoted in federation {}</b>',
        'fdemoted': '💼 <b><a href="{}">{}</a> demoted in federation {}</b>',

        'api_error': '🚫 <b>api.hikariatama.ru Error!</b>\n<code>{}</code>',
        'fsave_args': '💼 <b>Usage: .fsave shortname &lt;reply&gt;</b>',
        'fstop_args': '💼 <b>Usage: .fstop shortname</b>',
        'fsave': '💼 <b>Federative note </b><code>{}</code><b> saved!</b>',
        'fstop': '💼 <b>Federative note </b><code>{}</code><b> removed!</b>',
        'fnotes': '💼 <b>Federative notes:</b>\n{}',
        'usage': 'ℹ️ <b>Usage: .{} &lt;on/off&gt;</b>',
        'chat_only': 'ℹ️ <b>This command is for chats only</b>',

        'version': '''<b>📡 {}</b>

<b>😌 Author: @hikariatama</b>
<b>📥 Downloaded from @hikarimods</b>

<b>Licensed under Apache2.0 license
Distribution without author's permission and\\or watermarks is strictly forbidden</b>''',
        'error': '⛎ <b>HikariChat Issued error\nIt was reported to @hikariatama</b>',
        'reported': '💼 <b><a href="{}">{}</a> reported this message to admins\nReason: {}</b>'
    }

    def __init__(self):
        self.__doc__ = f"""
Advanced chat admin toolkit
Distributing without author's tag is strictly prohibited by license
This module is made by @hikariatama
Version: {version}"""

    async def client_ready(self,
                           client: "telethon.client.telegramclient.TelegramClient",
                           db: "friendly-telegram.database.frontend.Database") -> None:
        """Entry point"""
        global api

        def get_commands(mod) -> dict:
            """Introspect the module to get its commands"""
            # https://stackoverflow.com/a/34452/5509575
            return {method_name[:-3]: getattr(mod, method_name) for method_name in dir(mod)
                    if callable(getattr(mod, method_name)) and method_name[-3:] == "cmd"}

        self.db = db
        self.client = client

        self.me = str((await client.get_me()).id)

        self.warns = db.get('HikariChat', 'warns', {})

        self.ratelimit = {
            'notes': {}, 
            'report': {}
        }
        self._me = (await client.get_me()).id

        self.last_feds_update = 0
        self.last_chats_update = 0
        self.chats_update_delay = API_UPDATE_DELAY
        self.feds_update_delay = API_UPDATE_DELAY

        self.flood_timeout = FLOOD_TIMEOUT
        self.flood_threshold = FLOOD_TRESHOLD

        self.chats = {}
        self.my_protects = {}
        self.federations = {}
        self.prefix = utils.escape_html(
                            (db.get(main.__name__, "command_prefix", False) or ".")[0])

        self.api = api
        await api.init(client, db, self)

        try:
            self.flood_cache = json.loads(open('flood_cache.json', 'r').read())
        except Exception:
            self.flood_cache = {}

        await self.update_feds()

        commands = get_commands(self)
        for protection in ['antinsfw', 'antiarab', 'antitagall', 'antihelp', 'antiflood', 'antichannel', 'antispoiler', 'report']:
            commands[protection] = self.protection_template(protection)
        self.commands = commands

    def save_flood_cache(self) -> None:
        open('flood_cache.json', 'w').write(json.dumps(self.flood_cache))

    def chat_command(func):
        @functools.wraps(func)
        async def wrapped(*args, **kwargs):
            if len(args) < 2 or not isinstance(args[1], Message):
                return await func(*args, **kwargs)

            if args[1].is_private:
                await utils.answer(args[1], args[0].strings('chat_only'))
                return

            return await func(*args, **kwargs)

        wrapped.__doc__ = func.__doc__
        wrapped.__module__ = func.__module__

        return wrapped

    def error_handler(func):
        @functools.wraps(func)
        async def wrapped(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception:
                await api.report_error(traceback.format_exc())
                if func.__name__ == 'watcher':
                    return

                try:
                    await utils.answer(args[1], args[0].strings('error'))
                except Exception:
                    pass

        wrapped.__doc__ = func.__doc__
        wrapped.__module__ = func.__module__

        return wrapped

    @error_handler
    async def update_chats(self):
        if time.time() - self.last_chats_update < self.chats_update_delay:
            return

        self.last_chats_update = time.time()

        answ = await self.api.get('chats')

        if answ['success']:
            self.chats = answ['chats']
            self.my_protects = answ['my_protects']
        else:
            await self.client.send_message('@userbot_notifies_bot', self.strings('api_error').format(answ))

    @error_handler
    async def update_feds(self):
        if time.time() - self.last_feds_update < self.feds_update_delay:
            return

        self.last_feds_update = time.time()

        answ = await self.api.get('federations')

        if answ['success']:
            self.federations = answ['feds']

    @error_handler
    async def protect(self, message, protection):
        args = utils.get_args_raw(message)
        chat = utils.get_chat_id(message)
        if protection in ['antitagall', 'antiraid', 'antiarab', 'antiflood', 'antinsfw']:
            if args not in ['warn', 'ban', 'kick', 'mute', 'delmsg']:
                args = 'off'
                await utils.answer(message, self.strings(f'{protection}_off'))
            else:
                await utils.answer(message, self.strings(f'{protection}_on').format(args))

            answ = await self.api.post(f'chats/{chat}/protects/{protection}', json={
                'info': args
            })
        else:
            if args == 'on':
                await utils.answer(message, self.strings(f'{protection}_on'))
            elif args == 'off':
                await utils.answer(message, self.strings(f'{protection}_off').format(args))
            else:
                await utils.answer(message, self.strings('usage').format(protection))
                return

            answ = await self.api.post(f'chats/{chat}/protects/{protection}', json={
                'state': args
            })

        if not answ['success']:
            await utils.answer(message, self.strings('api_error').format(answ))
            return

    def protection_template(self, protection: str):
        comments = {
            'antinsfw': 'AntiNSFW',
            'antiarab': 'AntiArab',
            'antitagall': 'AntiTagAll',
            'antihelp': 'AntiHelp',
            'antiflood': 'AntiFlood',
            'antichannel': 'AntiChannel',
            'antispoiler': 'AntiSpoiler',
            'report': 'Report'
        }
        func_name = f"{protection}cmd"
        func = functools.partial(self.protect, protection=protection)
        func.__module__ = self.__module__
        func.__name__ = func_name
        func.__self__ = self
        func.__doc__ = f"<action> - Toggle {comments[protection]}"
        setattr(func, self.__module__ + "." + func.__name__, loader.support)
        return func

    @staticmethod
    def convert_time(t: str) -> int:
        if 'd' in str(t):
            t = int(t[:-1]) * 60 * 60 * 24
        if 'h' in str(t):
            t = int(t[:-1]) * 60 * 60
        if 'm' in str(t):
            t = int(t[:-1]) * 60
        if 's' in str(t):
            t = int(t[:-1])

        t = int(re.sub(r'[^0-9]', '', str(t)))

        return t

    async def ban(self, chat: Chat or int, user: User or Channel or int, period: int = 0) -> None:
        """Ban user in chat"""
        await self.client.edit_permissions(chat,
                                           user,
                                           until_date=(time.time() + period) if period else 0,
                                           view_messages=False,
                                           send_messages=False,
                                           send_media=False,
                                           send_stickers=False,
                                           send_gifs=False,
                                           send_games=False,
                                           send_inline=False,
                                           send_polls=False,
                                           change_info=False,
                                           invite_users=False)

    async def mute(self, chat: Chat or int, user: User or Channel or int, period: int = 0) -> None:
        """Mute user in chat"""
        await self.client.edit_permissions(chat,
                                           user,
                                           until_date=(time.time() + period) if period else 0,
                                           send_messages=False)

    async def args_parser_1(self, message: Message) -> tuple:
        """Get args from message
        user | time | reason"""
        t = message.raw_text
        try:
            args = t.split(maxsplit=1)[1]
        except Exception:
            args = ""

        reply = await message.get_reply_message()

        # .ban <reply>
        try:
            if not args and reply:
                user = await self.client.get_entity(reply.sender_id)
                t = 0
                reason = self.strings('no_reason')
                return user, t, reason
        except Exception as e:
            pass

        # .ban <user>

        try:
            if not reply and args:
                user = await self.client.get_entity(args)
                t = 0
                reason = self.strings('no_reason')
                return user, t, reason
        except Exception as e:
            pass

        # .ban <time> <reply>

        try:
            if reply and self.convert_time(args):
                user = await self.client.get_entity(args)
                t = self.convert_time(args)
                reason = self.strings('no_reason')
                return user, t, reason
        except Exception as e:
            pass

        # .ban <time> <user> [reason]

        try:
            if not reply and args:
                a = args.split(maxsplit=2)
                t = self.convert_time(a[0])
                user = await self.client.get_entity(a[1])
                reason = ' '.join(a[2:]) if len(
                    a) > 2 else self.strings('no_reason')
                return user, t, reason
        except Exception as e:
            pass

        # .ban <time> <reason>

        try:
            if reply and args:
                a = args.split(maxsplit=1)
                t = self.convert_time(a[0])
                user = await self.client.get_entity(reply.sender_id)
                reason = a[1] or self.strings('no_reason')
                return user, t, reason
        except Exception as e:
            pass

        return False

    async def args_parser_2(self, message: Message) -> tuple:
        t, reason = None, None
        args = utils.get_args_raw(message)
        if '-s' in args:
            args = args.replace('-s', '').replace('  ', ' ')
            silent = True
        else:
            silent = False
        reply = await message.get_reply_message()
        user = None
        if not reply:
            try:
                user, reason = args.split(maxsplit=1)
                user = await self.client.get_entity(user)
                t = 0
            except Exception:
                pass

            if not user:
                try:
                    user = await self.client.get_entity(args)
                except Exception:
                    await utils.answer(message, self.strings('args'))
                    return

                reason = self.strings('no_reason')
                t = 0
        else:
            user = await self.client.get_entity(reply.sender_id)
            reason = args or self.strings('no_reason')
            t = 0

        return user, t, reason, silent

    def find_fed(self, message: Message) -> None or str:
        """Find if chat belongs to any federation"""
        for federation, info in self.federations.items():
            if utils.get_chat_id(message) in info['chats']:
                return federation

        return None

    @error_handler
    async def punish(self, chat_id, user, violation, action, user_name):
        if action == "delmsg":
            comment = 'deteled message'
        elif action == "kick":
            comment = 'kicked him'
            await self.client.kick_participant(chat_id, user)
        elif action == "ban":
            comment = 'banned him for 1 hour'
            await self.ban(chat_id, user, 60 * 60)
        elif action == "mute":
            comment = 'muted him for 1 hour'
            await self.mute(chat_id, user, 60 * 60)

        elif action == "warn":
            comment = 'warned him'
            warn_msg = await self.client.send_message(chat_id, f'.warn {user.id} {violation}')
            await self.allmodules.commands['warn'](warn_msg)
        else:
            comment = 'just chill 😶‍🌫️'

        await self.client.send_message(chat_id,
                                       self.strings(violation)
                                           .format(
                                               get_link(user),
                                               user_name,
                                               comment
                                       )
                                       )

    @error_handler
    async def versioncmd(self, message: Message) -> None:
        """Get module info"""
        await utils.answer(message, self.strings('version').format(ver))

    @error_handler
    @chat_command
    async def newfedcmd(self, message: Message) -> None:
        """<shortname> <name> - Create new federation"""
        args = utils.get_args_raw(message)
        if not args or args.count(' ') == 0:
            await utils.answer(message, self.strings('args'))
            return

        shortname, name = args.split(maxsplit=1)
        if shortname in self.federations:
            await utils.answer(message, self.strings('fedexists'))
            return

        answ = await self.api.post('federations', json={
            'shortname': shortname,
            'name': name
        })

        if answ['success']:
            await self.update_feds()
            await utils.answer(message, self.strings('newfed').format(name))
        else:
            await utils.answer(message, self.strings('api_error').format(json.dumps(answ, indent=4)))

    @error_handler
    @chat_command
    async def rmfedcmd(self, message: Message) -> None:
        """<shortname> - Remove federation"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings('args'))
            return

        if args not in self.federations:
            await utils.answer(message, self.strings('fed404'))
            return

        name = self.federations[args]['name']

        answ = await self.api.delete(f'federations/{self.federations[args]["uid"]}')

        if answ['success']:
            await self.update_feds()
            await utils.answer(message, self.strings('rmfed').format(name))
        else:
            await utils.answer(message, self.strings('api_error').format(json.dumps(answ, indent=4)))

    @error_handler
    @chat_command
    async def fpromotecmd(self, message: Message) -> None:
        """<shortname> <reply|user> - Promote user in federation"""
        chat_id = utils.get_chat_id(message)
        fed = self.find_fed(message)

        if not fed:
            await utils.answer(message, self.strings('no_fed'))
            return

        reply = await message.get_reply_message()
        args = utils.get_args_raw(message)
        if not reply and not args:
            await utils.answer(message, self.strings('args'))
            return

        user = reply.sender_id if reply else args
        try:
            try:
                obj = await self.client.get_entity(user)
            except Exception:
                await utils.answer(message, self.strings('args'))
                return

            name = get_full_name(obj)
        except Exception:
            await utils.answer(message, self.strings('args'))
            return

        answ = await self.api.post(f'federations/{self.federations[fed]["uid"]}/promote', json={
            'user': obj.id
        })

        if answ['success']:
            await self.update_feds()
            await utils.answer(message,
                               self.strings('fpromoted').format(get_link(obj), name, self.federations[fed]['name']))
        else:
            await utils.answer(message, self.strings('api_error').format(json.dumps(answ, indent=4)))

    @error_handler
    @chat_command
    async def fdemotecmd(self, message: Message) -> None:
        """<shortname> <reply|user> - Demote user in federation"""
        chat_id = utils.get_chat_id(message)
        fed = self.find_fed(message)

        if not fed:
            await utils.answer(message, self.strings('no_fed'))
            return

        reply = await message.get_reply_message()
        args = utils.get_args_raw(message)
        if not reply and not args:
            await utils.answer(message, self.strings('args'))
            return

        user = reply.sender_id if reply else args
        try:
            try:
                obj = await self.client.get_entity(user)
            except Exception:
                await utils.answer(message, self.strings('args'))
                return

            user = obj.id

            name = get_full_name(user)
        except Exception:
            name = 'User'

        answ = await self.api.post(f'federations/{self.federations[fed]["uid"]}/demote', json={
            'user': user
        })

        if answ['success']:
            await self.update_feds()
            await utils.answer(message, self.strings('fdemoted').format(user, name, self.federations[fed]['name']))
        else:
            await utils.answer(message, self.strings('api_error').format(json.dumps(answ, indent=4)))

    @error_handler
    @chat_command
    async def faddcmd(self, message: Message) -> None:
        """<fed name> - Add chat to federation"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings('args'))
            return

        if args not in self.federations:
            await utils.answer(message, self.strings('fed404'))
            return

        chat = utils.get_chat_id(message)

        answ = await self.api.post(f'federations/{self.federations[args]["uid"]}/chats', json={
            'cid': chat
        })

        if not answ['success']:
            await utils.answer(message, self.strings('api_error').format(json.dumps(answ, indent=4)))
            return

        await self.update_feds()

        await utils.answer(message, self.strings('fadded').format(self.federations[args]['name']))

    @error_handler
    @chat_command
    async def frmcmd(self, message: Message) -> None:
        """<fed name> - Remove chat from federation"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings('args'))
            return

        if args not in self.federations:
            await utils.answer(message, self.strings('fed404'))
            return

        chat = utils.get_chat_id(message)

        answ = await self.api.delete(f'federations/{self.federations[args]["uid"]}/chats', json={
            'cid': chat
        })

        if answ['success']:
            await self.update_feds()
            await utils.answer(message, self.strings('frem').format(self.federations[args]['name']))
        else:
            await utils.answer(message, self.strings('api_error').format(json.dumps(answ, indent=4)))

    @error_handler
    @chat_command
    async def fbancmd(self, message: Message) -> None:
        """<reply | user> <reason | optional> [-s silent] - Ban user in federation"""
        chat_id = utils.get_chat_id(message)
        fed = self.find_fed(message)

        if not fed:
            await utils.answer(message, self.strings('no_fed'))
            return

        a = await self.args_parser_2(message)
        if not a:
            await utils.answer(message, self.strings('args'))
            return

        user, t, reason, silent = a

        answ = await self.api.get(f'federations/{self.federations[fed]["uid"]}/chats')

        if not answ['success']:
            await utils.answer(message, self.strings('api_error').format(json.dumps(answ, indent=4)))
            return

        chats = answ['chats']

        banned_in = []

        for c in chats:
            try:
                chat = await self.client.get_entity(c)
            except Exception:
                continue

            if not chat.admin_rights and not chat.creator:
                continue

            try:
                await self.client.edit_permissions(chat, user, until_date=time.time() + t, view_messages=False,
                                                   send_messages=False, send_media=False, send_stickers=False,
                                                   send_gifs=False, send_games=False, send_inline=False,
                                                   send_polls=False,
                                                   change_info=False, invite_users=False)
                if chat.id != chat_id and not silent:
                    await self.client.send_message(chat, self.strings('fban').format(get_link(user),
                                                                                     get_first_name(
                                                                                         user),
                                                                                     self.federations[fed][
                                                                                         'name'], reason))

                banned_in += [chat.title]
            except UserAdminInvalidError:
                pass

        await utils.answer(message, self.strings('fban').format(get_link(user), get_first_name(user),
                                                                self.federations[fed]['name'],
                                                                reason) + '\n\n<b>' + '\n'.join(banned_in) + '</b>')

        await self.api.delete(f'federations/{self.federations[fed]["uid"]}/clrwarns', json={
            'user': str(user.id)
        })

        reply = await message.get_reply_message()
        if reply:
            await reply.delete()

    @error_handler
    @chat_command
    async def kickcmd(self, message: Message) -> None:
        """<reply | user> <reason | optional> - Kick user"""
        chat = await message.get_chat()

        if not chat.admin_rights and not chat.creator:
            await utils.answer(message, self.strings('not_admin'))
            return

        reply = await message.get_reply_message()
        args = utils.get_args_raw(message)
        user, reason = None, None

        try:
            if reply:
                user = await self.client.get_entity(reply.sender_id)
                reason = args or self.strings
            else:
                uid = args.split(maxsplit=1)[0]
                try:
                    uid = int(uid)
                except Exception:
                    pass
                user = await self.client.get_entity(uid)
                reason = args.split(maxsplit=1)[1] if len(
                    args.split(maxsplit=1)) > 1 else self.strings('no_reason')
        except Exception:
            await utils.answer(message, self.strings('args'))
            return

        try:
            await self.client.kick_participant(utils.get_chat_id(message), user)
            await utils.answer(message,
                               self.strings('kick').format(get_link(user), get_first_name(user),
                                                           reason))
        except UserAdminInvalidError:
            await utils.answer(message, self.strings('not_admin'))
            return

    @error_handler
    @chat_command
    async def bancmd(self, message: Message) -> None:
        """<reply | user> <reason | optional> - Ban user"""
        chat = await message.get_chat()

        a = await self.args_parser_2(message)
        if not a:
            await utils.answer(message, self.strings('args'))
            return

        user, t, reason, silent = a

        if not chat.admin_rights and not chat.creator:
            await utils.answer(message, self.strings('not_admin'))
            return

        try:
            await self.ban(chat, user, t)
            await utils.answer(message, self.strings('ban').format(get_link(user),
                                                                   get_first_name(
                                                                       user),
                                                                   f'for {t // 60} min(-s)' if t != 0 else 'forever',
                                                                   reason))
        except UserAdminInvalidError:
            await utils.answer(message, self.strings('not_admin'))
            return

    @error_handler
    @chat_command
    async def mutecmd(self, message: Message) -> None:
        """<reply | user> <time | 0 for infinity> <reason | optional> - Mute user"""
        chat = await message.get_chat()

        a = await self.args_parser_1(message)
        if not a:
            await utils.answer(message, self.strings('args'))
            return

        user, t, reason = a

        if not chat.admin_rights and not chat.creator:
            await utils.answer(message, self.strings('not_admin'))
            return

        try:
            await self.client.edit_permissions(chat, user, until_date=time.time() + t, send_messages=False)
            await utils.answer(message,
                               self.strings('mute').format(get_link(user), get_first_name(user),
                                                           f'for {t // 60} min(-s)' if t != 0 else 'forever',
                                                           reason))
        except UserAdminInvalidError:
            await utils.answer(message, self.strings('not_admin'))
            return

    @error_handler
    @chat_command
    async def unmutecmd(self, message: Message) -> None:
        """<reply | user> - Unmute user"""
        chat = await message.get_chat()

        if not chat.admin_rights and not chat.creator:
            await utils.answer(message, self.strings('not_admin'))
            return

        reply = await message.get_reply_message()
        args = utils.get_args_raw(message)
        user = None

        try:
            if args.isdigit():
                args = int(args)
            user = await self.client.get_entity(args)
        except Exception:
            try:
                user = await self.client.get_entity(reply.sender_id)
            except Exception:
                await utils.answer(message, self.strings('args'))
                return

        try:
            await self.client.edit_permissions(chat, user, until_date=0, send_messages=True)
            await utils.answer(message, self.strings('unmuted')
                               .format(
                get_link(user),
                get_first_name(user)
            )
            )
        except UserAdminInvalidError:
            await utils.answer(message, self.strings('not_admin'))
            return

    @error_handler
    @chat_command
    async def unbancmd(self, message: Message) -> None:
        """<reply | user> - Unban user"""
        chat = await message.get_chat()

        if not chat.admin_rights and not chat.creator:
            await utils.answer(message, self.strings('not_admin'))
            return

        reply = await message.get_reply_message()
        args = utils.get_args_raw(message)
        user = None

        try:
            if args.isdigit():
                args = int(args)
            user = await self.client.get_entity(args)
        except Exception:
            try:
                user = await self.client.get_entity(reply.sender_id)
            except Exception:
                await utils.answer(message, self.strings('args'))
                return

        try:
            await self.client.edit_permissions(chat, user, until_date=0, view_messages=True, send_messages=True,
                                               send_media=True, send_stickers=True, send_gifs=True, send_games=True,
                                               send_inline=True, send_polls=True, change_info=True, invite_users=True)
            await utils.answer(message,
                               self.strings('unban').format(get_link(user), get_first_name(user)))
        except UserAdminInvalidError:
            await utils.answer(message, self.strings('not_admin'))
            return

    @error_handler
    async def protectscmd(self, message: Message) -> None:
        """List available filters"""
        await utils.answer(message, self.strings('protections'))

    @error_handler
    async def fedscmd(self, message: Message) -> None:
        """List federations"""
        res = self.strings('feds_header')
        await self.update_feds()
        for shortname, config in self.federations.copy().items():
            res += f"    ☮️ <b>{config['name']}</b> (<code>{shortname}</code>)"
            for chat in config['chats']:
                try:
                    c = await self.client.get_entity(chat)
                except Exception:
                    continue

                res += f"\n        <b>- <a href=\"tg://resolve?domain={getattr(c, 'username', '')}\">{c.title}</a></b>"

            res += f"\n        <b>👮‍♂️ {len(config['warns'])} warns</b>\n\n"

        await utils.answer(message, res)

    @error_handler
    @chat_command
    async def fedcmd(self, message: Message) -> None:
        """<shortname> - Info about federation"""
        args = utils.get_args_raw(message)
        chat = utils.get_chat_id(message)

        await self.update_feds()

        fed = self.find_fed(message)

        if (not args or args not in self.federations) and not fed:
            await utils.answer(message, self.strings('no_fed'))
            return

        if not args or args not in self.federations:
            args = fed

        res = self.strings('fed')

        fed = args

        admins = ""
        for admin in self.federations[fed]['admins']:
            try:
                user = await self.client.get_entity(int(admin))
            except Exception:
                continue
            name = get_full_name(user)
            admins += f" <b>👤 <a href=\"{get_link(user)}\">{name}</a></b>\n"

        chats = ""
        for chat in self.federations[fed]['chats']:
            try:
                c = await self.client.get_entity(chat)
            except Exception:
                continue

            chats += f" <b>🫂 <a href=\"tg://resolve?domain={getattr(c, 'username', '')}\">{c.title}</a></b>\n"

        await utils.answer(message, res.format(self.federations[fed]['name'], chats, admins,
                                               len(self.federations[fed]['warns'])))

    @error_handler
    @chat_command
    async def pchatcmd(self, message: Message) -> None:
        """List protection for current chat"""

        chat_id = str(utils.get_chat_id(message))
        await self.update_chats()
        if chat_id not in self.chats or not self.chats[chat_id]:
            await utils.answer(message, self.strings('chat404'))
            return

        res = f"📡 <b>{ver}</b>\n"

        answ = await self.api.get(f'chats/{chat_id}/protects')

        if not answ['success']:
            await utils.answer(message, self.strings('api_error').format(answ))
            return

        obj = answ['protects']

        fed = self.find_fed(message)

        res += "\n🚪 <b>AntiRaid</b> Action: <b>{} all joined</b>".format(
            obj['antiraid']) if 'antiraid' in obj else ""
        res += "\n🐵 <b>AntiTagAll.</b> Action: <b>{}</b>".format(
            obj['antitagall']) if 'antitagall' in obj else ""
        res += "\n🐻 <b>AntiArab.</b> Action: <b>{}</b>".format(
            obj['antiarab']) if 'antiarab' in obj else ""
        res += "\n⏱ <b>AntiFlood</b> Action: <b>{}</b>".format(
            obj['antiflood']) if 'antiflood' in obj else ""
        res += "\n📯 <b>AntiChannel.</b>" if 'antichannel' in obj else ""
        res += "\n🪙 <b>AntiSpoiler.</b>" if 'antispoiler' in obj else ""
        res += "\n🍓 <b>AntiNSFW.</b> Action: <b>{}</b>".format(obj['antinsfw']) if 'antinsfw' in obj else ""
        res += "\n🐺 <b>AntiHelp.</b>" if 'antihelp' in obj else ""
        res += "\n💼 <b>Federation: </b>" + \
            self.federations[fed]['name'] if fed is not None else ""
        res += "\n👋 <b>Welcome.</b> \n{}".format(
            obj['welcome']) if 'welcome' in obj else ""

        await utils.answer(message, res)

    @error_handler
    @chat_command
    async def warncmd(self, message: Message) -> None:
        """<reply | user_id | username> <reason | optional> - Warn user"""
        chat = await message.get_chat()

        if not chat.admin_rights and not chat.creator:
            await utils.answer(message, self.strings('not_admin'))
            return

        chat_id = utils.get_chat_id(message)
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        user = None
        if reply:
            user = await self.client.get_entity(reply.sender_id)
            reason = args or self.strings('no_reason')
        else:
            try:
                u = args.split(maxsplit=1)[0]
                try:
                    u = int(u)
                except Exception:
                    pass

                user = await self.client.get_entity(u)
            except IndexError:
                await utils.answer(message, self.strings('args'))
                return

            try:
                reason = args.split(maxsplit=1)[1]
            except IndexError:
                reason = self.strings('no_reason')

        fed = self.find_fed(message)

        if not fed:
            await utils.answer(message, self.strings('no_fed'))
            return

        answ = await self.api.post(f'federations/{self.federations[fed]["uid"]}/warn', json={
            'user': str(user.id),
            'reason': reason
        })

        if not answ['success']:
            await utils.answer(message, self.strings('api_error').format(json.dumps(answ, indent=4)))
            return

        await self.update_feds()

        warns = answ['user_warns']

        if len(warns) >= 7:
            user_name = get_first_name(user)
            answ = await self.api.get(f'federations/{self.federations[fed]["uid"]}/chats')

            if not answ['success']:
                await utils.answer(message, self.strings('api_error').format(json.dumps(answ, indent=4)))
                return

            chats = answ['chats']
            for c in chats:
                await self.client(
                    EditBannedRequest(
                        c,
                        user,
                        ChatBannedRights(
                            until_date=time.time() + 60 ** 2 * 24,
                            send_messages=True,
                        ),
                    )
                )

                await self.client.send_message(c, self.strings('warns_limit').format(get_link(user), user_name,
                                                                                     'muted him in federation for 24 hours'))

            await message.delete()

            answ = await self.api.delete(f'federations/{self.federations[fed]["uid"]}/clrwarns',
                                         json={
                                             'user': str(user.id)
                                         })
        else:
            await utils.answer(message,
                               self.strings('fwarn', message).format(get_link(user),
                                                                     get_first_name(
                                                                         user),
                                                                     len(warns),
                                                                     7, reason))

    @error_handler
    @chat_command
    async def warnscmd(self, message: Message) -> None:
        """<reply | user_id | username | optional> - Show warns in chat \\ of user"""
        chat_id = utils.get_chat_id(message)

        fed = self.find_fed(message)

        async def check_admin(user_id):
            try:
                return (await self.client.get_permissions(chat_id, user_id)).is_admin
            except ValueError:
                return (
                    user_id in loader.dispatcher.security._owner or user_id in loader.dispatcher.security._sudo)

        async def check_member(user_id):
            try:
                await self.client.get_permissions(chat_id, user_id)
                return True
            except Exception:
                return False

        if not fed:
            await utils.answer(message, self.strings('no_fed'))
            return

        answ = await self.api.get(f'federations/{self.federations[fed]["uid"]}/warns')

        if not answ['success']:
            await utils.answer(message, self.strings('api_error').format(json.dumps(answ, indent=4)))
            return

        await self.update_feds()

        warns = answ['warns']

        if not warns:
            await utils.answer(message, self.strings('no_fed_warns'))
            return

        async def send_user_warns(usid):
            try:
                if int(usid) < 0:
                    usid = int(str(usid)[4:])
            except Exception:
                pass
            if not warns:
                await utils.answer(message, self.strings('no_fed_warns'))
                return

            elif str(usid) not in warns or not warns[str(usid)]:
                user_obj = await self.client.get_entity(usid)
                await utils.answer(message, self.strings('no_warns').format(get_link(user_obj),
                                                                            get_full_name(user_obj)))
            else:
                user_obj = await self.client.get_entity(usid)
                await utils.answer(message, self.strings('warns').format(get_link(user_obj),
                                                                         get_full_name(
                                                                             user_obj),
                                                                         len(warns[str(
                                                                             usid)]), 7,
                                                                         '\n    🏴󠁧󠁢󠁥󠁮󠁧󠁿 '.join(warns[str(usid)])))

        if not await check_admin(message.sender_id):
            await send_user_warns(message.sender_id)
        else:
            reply = await message.get_reply_message()
            args = utils.get_args_raw(message)
            if not reply and not args:
                res = self.strings('warns_adm_fed')
                for user, _warns in warns.copy().items():
                    try:
                        user_obj = await self.client.get_entity(int(user))
                    except Exception:
                        continue

                    if isinstance(user_obj, User):
                        try:
                            name = get_full_name(user_obj)
                        except TypeError:
                            continue
                    else:
                        name = user_obj.title

                    res += f"🐺 <b><a href=\"{get_link(user_obj)}\">" + name + '</a></b>\n'
                    for warn in _warns:
                        res += "<code>   </code>🏴󠁧󠁢󠁥󠁮󠁧󠁿 <i>" + warn + '</i>\n'

                await utils.answer(message, res)
                return
            elif reply:
                await send_user_warns(reply.sender_id)
            elif args:
                await send_user_warns(args)

    @error_handler
    @chat_command
    async def dwarncmd(self, message: Message) -> None:
        """<reply | user_id | username> - Remove last warn"""
        chat_id = str(utils.get_chat_id(message))
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        user = None

        if reply:
            user = await self.client.get_entity(reply.sender_id)
        else:
            try:
                args = int(args)
            except Exception:
                pass

            try:
                user = await self.client.get_entity(args)
            except IndexError:
                await utils.answer(message, self.strings('args'))
                return

        fed = self.find_fed(message)

        if not fed:
            await utils.answer(message, self.strings('no_fed'))
            return

        answ = await self.api.delete(f'federations/{self.federations[fed]["uid"]}/warn',
                                     json={
                                         'user': str(user.id)
                                     })
        if answ['success']:
            await self.update_feds()
            await utils.answer(message, self.strings('dwarn_fed').format(get_link(user),
                                                                         get_first_name(user)))
        else:
            await utils.answer(message, self.strings('api_error').format(json.dumps(answ, indent=4)))
            return

    @error_handler
    @chat_command
    async def clrwarnscmd(self, message: Message) -> None:
        """<reply | user_id | username> - Remove all warns from user"""
        chat_id = str(utils.get_chat_id(message))
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        user = None
        if reply:
            user = await self.client.get_entity(reply.sender_id)
        else:
            try:
                args = int(args)
            except Exception:
                pass

            try:
                user = await self.client.get_entity(args)
            except IndexError:
                await utils.answer(message, self.strings('args'))
                return

        fed = self.find_fed(message)

        if not fed:
            await utils.answer(message, self.strings('no_fed'))
            return

        answ = await self.api.delete(f'federations/{self.federations[fed]["uid"]}/clrwarns',
                                     json={
                                         'user': str(user.id)
                                     })
        if answ['success']:
            await self.update_feds()
            await utils.answer(message, self.strings('clrwarns_fed').format(get_link(user),
                                                                            get_first_name(user)))
        else:
            await utils.answer(message, self.strings('api_error').format(json.dumps(answ, indent=4)))
            return

    @error_handler
    @chat_command
    async def welcomecmd(self, message: Message) -> None:
        """<text> - Change welcome text"""
        chat_id = utils.get_chat_id(message)
        args = utils.get_args_raw(message) or ''

        answ = await self.api.post(f'chats/{chat_id}/welcome', json={
            'state': args
        })

        if not answ['success']:
            await utils.answer(message, self.strings('api_error').format(answ))
            return

        if args:
            await utils.answer(message, self.strings('welcome').format(args))
        else:
            await utils.answer(message, self.strings('unwelcome'))

    @error_handler
    @chat_command
    async def fdefcmd(self, message: Message) -> None:
        """<user | reply> - Toggle global user invulnerability"""
        chat_id = utils.get_chat_id(message)

        fed = self.find_fed(message)

        if not fed:
            await utils.answer(message, self.strings('no_fed'))
            return

        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        user = None
        if reply:
            user = await self.client.get_entity(reply.sender_id)
        else:
            try:
                args = int(args)
            except Exception:
                pass

            try:
                user = await self.client.get_entity(args)
            except Exception:
                await utils.answer(message, self.strings('args'))
                return

        answ = await self.api.post(f'federations/{self.federations[fed]["uid"]}/fdef',
                                   json={
                                       'user': user.id
                                   })

        if not answ['success']:
            await utils.answer(message, self.strings('api_error').format(answ))
            return

        await self.update_feds()

        await utils.answer(message,
                           self.strings('defense').format(get_link(user), get_first_name(user),
                                                          'on' if answ['status'] else 'off'))

    @error_handler
    @chat_command
    async def fsavecmd(self, message: Message) -> None:
        """<note name> <reply> - Save federative note"""
        chat_id = utils.get_chat_id(message)

        fed = self.find_fed(message)

        if not fed:
            await utils.answer(message, self.strings('no_fed'))
            return

        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        if not reply or not args or not reply.text:
            await utils.answer(message, self.strings('fsave_args'))
            return

        answ = await self.api.post(f'federations/{self.federations[fed]["uid"]}/notes',
                                   json={
                                       'shortname': args,
                                       'note': reply.text
                                   })

        if not answ['success']:
            await utils.answer(message, self.strings('api_error').format(answ))
            return

        await self.update_feds()

        await utils.answer(message, self.strings('fsave').format(args))

    @error_handler
    @chat_command
    async def fstopcmd(self, message: Message) -> None:
        """<note name> - Remove federative note"""
        chat_id = utils.get_chat_id(message)

        fed = self.find_fed(message)

        if not fed:
            await utils.answer(message, self.strings('no_fed'))
            return

        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings('fsop_args'))
            return

        answ = await self.api.delete(f'federations/{self.federations[fed]["uid"]}/notes',
                                     json={
                                         'shortname': args
                                     })

        if not answ['success']:
            await utils.answer(message, self.strings('api_error').format(answ))
            return

        await self.update_feds()

        await utils.answer(message, self.strings('fstop').format(args))

    @error_handler
    @chat_command
    async def fnotescmd(self, message: Message, from_watcher: bool = False) -> None:
        """Show federative notes"""
        chat_id = utils.get_chat_id(message)

        fed = self.find_fed(message)

        if not fed:
            await utils.answer(message, self.strings('no_fed'))
            return

        answ = await self.api.get(f'federations/{self.federations[fed]["uid"]}/notes')

        if not answ['success']:
            await utils.answer(message, self.strings('api_error').format(answ))
            return

        res = {}

        notes = ""
        for shortname, note in answ['notes'].items():
            if int(note['creator']) != self._me and from_watcher:
                continue

            try:
                obj = await self.client.get_entity(int(note['creator']))
                name = obj.first_name or obj.title
                key = f"<a href=\"{get_link(obj)}\">{name}</a>"
                if key not in res:
                    res[key] = ""
                res[key] += f"  <code>{shortname}</code>\n"
            except Exception:
                key = f"unknown"
                if key not in res:
                    res[key] = ""
                res[key] += f"  <code>{shortname}</code>\n"

        for owner, note in res.items():
            notes += f"\nby {owner}:\n{note}"

        if not notes:
            return

        await utils.answer(message, self.strings('fnotes').format(notes))

    @error_handler
    @chat_command
    async def fdeflistcmd(self, message: Message) -> None:
        """Show global invulnerable users"""
        chat_id = utils.get_chat_id(message)

        fed = self.find_fed(message)

        if not fed:
            await utils.answer(message, self.strings('no_fed'))
            return

        answ = await self.api.get(f'federations/{self.federations[fed]["uid"]}/fdef')

        if not answ['success']:
            await utils.answer(message, self.strings('api_error').format(answ))
            return

        if not answ['fdef']:
            await utils.answer(message, self.strings('no_defense'))
            return

        res = ""
        defense = answ['fdef']
        for user in defense.copy():
            try:
                u = await self.client.get_entity(user)
            except Exception:
                await self.api.post(f'federations/{self.federations[fed]["uid"]}/fdef',
                                    json={
                                        'user': user
                                    })
                await asyncio.sleep(.2)
                continue

            tit = get_full_name(u)

            res += f"  🇻🇦 <a href=\"{get_link(u)}\">{tit}</a>\n"

        await utils.answer(message, self.strings('defense_list').format(res))
        return

    @error_handler
    async def watcher(self, message) -> None:
        if not (
                isinstance(getattr(message, 'chat', 0), Chat) or \
                isinstance(getattr(message, 'chat', 0), Channel) and getattr(message.chat, 'megagroup', False)
                ):
            return

        chat_id = utils.get_chat_id(message)
        try:
            user_id = getattr(message, 'sender_id', False) or message.action_message.action.users[0]
        except Exception:
            try:
                user_id = message.action_message.action.from_id.user_id
            except Exception:
                try:
                    user_id = message.from_id.user_id
                except Exception:
                    await self.api.report_error(str(message))
                    return


        user_id = int(str(user_id)[4:]) if str(user_id).startswith('-100') else int(user_id)

        violation = None
        action = None

        fed = self.find_fed(message)

        if getattr(message, 'raw_text', False):
            if fed in self.federations:
                if user_id and isinstance(message, Message):
                    if str(user_id) not in self.ratelimit['notes'] or \
                        self.ratelimit['notes'][str(user_id)] < time.time():
                        if not (message.raw_text.startswith(self.prefix) and len(message.raw_text) > 1 and \
                                message.raw_text[1] != self.prefix):
                            await self.update_feds()
                            if message.raw_text == "#заметки" or message.raw_text == "#notes":
                                self.ratelimit['notes'][str(user_id)] = time.time() + 3
                                await self.fnotescmd(await message.reply(f'<code>{self.prefix}fnotes</code>'), True)

                            for note, note_info in self.federations[fed]['notes'].items():
                                if str(note_info['creator']) != str(self._me):
                                    continue

                                if note.lower() in message.raw_text.lower():
                                    await utils.answer(message, note_info['text'])
                                    self.ratelimit['notes'][str(user_id)] = time.time() + 3


                if user_id in self.federations[fed]['fdef']:
                    return

        if user_id < 0:
            user_id = int(str(user_id)[4:])

        await self.update_chats()
        if str(chat_id) not in self.chats or not self.chats[str(chat_id)]:
            return

        if str(chat_id) not in self.my_protects:
            return

        try:
            if (await self.client.get_permissions(chat_id, message.sender_id)).is_admin:
                return
        except Exception:
            pass

        user = await self.client.get_entity(user_id)
        chat = await message.get_chat()
        user_name = get_full_name(user)

        # Anti Raid:

        if 'antiraid' in self.chats[str(chat_id)] and 'antiraid' in self.my_protects[str(chat_id)]:
            if getattr(message, "user_joined", False) or getattr(message, "user_added", False):
                action = self.chats[str(chat_id)]['antiraid']
                if action == "kick":
                    await self.client.send_message('me',
                                                   self.strings('antiraid').format('kicked', user.id,
                                                                                   user_name,
                                                                                   chat.title))
                    await self.client.kick_participant(chat_id, user)
                elif action == "ban":
                    await self.client.send_message('me',
                                                   self.strings('antiraid').format('banned', user.id,
                                                                                   user_name,
                                                                                   chat.title))
                    await self.ban(chat, user)
                elif action == "mute":
                    await self.client.send_message('me',
                                                   self.strings('antiraid').format('muted', user.id, user_name,
                                                                                   chat.title))
                    await self.mute(chat, user)

                return

        # Welcome:

        if 'welcome' in self.chats[str(chat_id)] and 'welcome' in self.my_protects[str(chat_id)]:
            if getattr(message, "user_joined", False) or getattr(message, "user_added", False):
                await self.client.send_message(chat_id,
                                               self.chats[str(chat_id)]['welcome']
                                               .replace('{user}', user_name)
                                               .replace('{chat}', chat.title)
                                               .replace('{mention}', f'<a href="{get_link(user)}">{user_name}</a>'),
                                               reply_to=message.action_message.id)

                return


        if getattr(message, 'action', ''):
            return

        # Report:
        if 'report' in self.chats[str(chat_id)] and 'report' in self.my_protects[str(chat_id)]:
            reply = await message.get_reply_message()
            if str(user_id) not in self.ratelimit['report'] or \
                self.ratelimit['report'][str(user_id)] < time.time():
                if message.raw_text.startswith('#report') and reply:
                    reason = message.raw_text.split(maxsplit=1)[1] if message.raw_text.count(' ') >= 1 else self.strings('no_reason')
                    answ = await self.api.post(f'chats/{chat_id}/report', json={
                        'reason': reason,
                        'link': await get_message_link(reply, chat),
                        'user_link': get_link(user),
                        'user_name': get_full_name(user),
                        'text_thumbnail': reply.raw_text[:1024]
                    })
                    if not answ['success']:
                        await utils.answer(message, self.strings('api_error').format(answ))
                        return

                    await utils.answer(reply, self.strings('reported').format(
                        get_link(user),
                        get_full_name(user),
                        reason
                    ))

                    self.ratelimit['report'][str(user_id)] = time.time() + 60
                    
                    await message.delete()



        # AntiChannel:

        if 'antichannel' in self.chats[str(chat_id)] and 'antichannel' in self.my_protects[str(chat_id)]:
            if getattr(message, 'sender_id', 0) < 0:
                await message.delete()
                return

        # AntiSpoiler:

        if 'antispoiler' in self.chats[str(chat_id)] and 'antispoiler' in self.my_protects[str(chat_id)]:
            if isinstance(getattr(message, 'entities'), list) and \
               any([isinstance(_, MessageEntitySpoiler) for _ in message.entities]):
                await message.delete()
                return

        # AntiFlood:

        if 'antiflood' in self.chats[str(chat_id)] and 'antiflood' in self.my_protects[str(chat_id)]:
            if str(chat_id) not in self.flood_cache:
                self.flood_cache[str(chat_id)] = {}

            if str(user_id) not in self.flood_cache[str(chat_id)]:
                self.flood_cache[str(chat_id)][str(user_id)] = []

            for item in self.flood_cache[str(chat_id)][str(user_id)].copy():
                if time.time() - item > self.flood_timeout:
                    self.flood_cache[str(chat_id)][str(
                        user_id)].remove(item)

            self.flood_cache[str(chat_id)][str(user_id)].append(
                round(time.time(), 2))
            self.save_flood_cache()

            if len(self.flood_cache[str(chat_id)][str(user_id)]) >= self.flood_threshold:
                del self.flood_cache[str(chat_id)][str(user_id)]
                violation = 'flood'
                action = self.chats[str(chat_id)]['antiflood']

        # AntiNSFW:

        if 'antinsfw' in self.chats[str(chat_id)] and 'antinsfw' in self.my_protects[str(chat_id)]:
            media = False

            if getattr(message, 'sticker', False):
                media = message.sticker
            elif getattr(message, 'media', False):
                media = message.media
            
            if media:
                photo = io.BytesIO()
                await self.client.download_media(message.media, photo)
                photo.seek(0)

                if imghdr.what(photo) in ['png', 'jpg', 'jpeg', 'tiff', 'bmp', 'webp', 'gif']:
                    response = await self.api.post('check_nsfw', data={'file': photo})
                    if response['verdict'] == 'nsfw':
                        todel = []
                        async for _ in self.client.iter_messages(message.peer_id, reverse=True,
                                                                 offset_id=message.id - 1):
                            todel += [_]
                            if _.sender_id != message.sender_id:
                                break

                        await self.client.delete_messages(message.peer_id, message_ids=todel, revoke=True)
                        violation = 'nsfw_content'
                        action = self.chats[str(chat_id)]['antinsfw']

        # AntiTagAll:

        if 'antitagall' in self.chats[str(chat_id)] and 'antitagall' in self.my_protects[str(chat_id)]:
            if message.text.count('tg://user?id=') >= 5:
                violation = 'tagall'
                action = self.chats[str(chat_id)]['antitagall']

        # AntiHelp:
        if 'antihelp' in self.chats[str(chat_id)] and 'antihelp' in self.my_protects[str(chat_id)]:
            search = message.text
            if '@' in search:
                search = search[:search.find('@')]
                tagged = True
            else:
                tagged = False

            blocked_commands = ['help', 'dlmod',
                                'loadmod', 'lm', 'ping', 'speedtest']

            if len(search.split()) > 0 and search.split()[0][1:] in blocked_commands:
                await message.delete()

        # AntiArab:
        if 'antiarab' in self.chats[str(chat_id)] and 'antiarab' in self.my_protects[str(chat_id)]:
            if getattr(message, "user_joined", False) or getattr(message, "user_added", False):
                if len(re.findall('[\u4e00-\u9fff]+', user_name)) != 0 or \
                   len(re.findall('[\u0621-\u064A]+', user_name)) != 0:
                    violation = 'arabic_nickname'
                    action = self.chats[str(chat_id)]['antiarab']

        if not violation:
            return

        await self.punish(chat_id, user, violation, action, user_name)

        try:
            await message.delete()
        except Exception: pass
