"""
    Copyright 2021 t.me/innocoffee
    Licensed under the Apache License, Version 2.0
    
    Author is not responsible for any consequencies caused by using this
    software or any of its parts. If you have any questions or wishes, feel
    free to contact Dan by sending pm to @innocoffee_alt.
"""

#<3 title: RPMod
#<3 pic: https://img.icons8.com/fluency/48/000000/tongue-out.png
#<3 desc: RPMod от Innomods

from .. import loader, utils

@loader.tds
class RPMod(loader.Module):
    """RPMod от Innomods"""
    strings = {
        'name': 'RPMod',
        'args': '🦊 <b>Incorrect args</b>',
        'success': '🦊 <b>Success</b>',
        'rplist': '🦊 <b>Current RP commands</b>\n\n{}'
    }

    async def client_ready(self, client, db):
        self.db = db
        self.client = client
        self.rp = db.get('RPMod', 'rp', {})
        self.chats = db.get('RPMod', 'active', [])

    async def rpcmd(self, message):
        """.rp <command> <message> - Add RP Command. If message unspecified, remove command"""
        args = utils.get_args_raw(message)
        try:
            command, msg = args.split(' ', 1)
        except:
            if not args or command not in self.rp:
                await utils.answer(message, self.strings('args', message))
                return
            else:
                del self.rp[command]
                self.db.set('RPMod', 'rp', self.rp)
                await utils.answer(message, self.strings('success', message))
                return

        self.rp[command] = msg
        self.db.set('RPMod', 'rp', self.rp)
        await utils.answer(message, self.strings('success', message))


    async def rptogglecmd(self, message):
        """.rptoggle - Toggle RP Mode in current chat"""
        cid = str(utils.get_chat_id(message))
        if cid in self.chats:
            self.chats.remove(cid)
        else:
            self.chats.append(cid)
        self.db.set('RPMod', 'active', self.chats)
        await utils.answer(message, self.strings('success', message))


    async def rplistcmd(self, message):
        """.rplist - List RP Commands"""
        await utils.answer(message, self.strings('rplist').format('\n'.join([f"    🇨🇭 {command} - {msg}" for command, msg in self.rp.items()])))

    
    async def watcher(self, message):
        try:
            cid = str(utils.get_chat_id(message))
            if cid not in self.chats:
                return

            if message.text.split(' ', 1)[0] not in self.rp:
                return

            cmd = message.text.split(' ', 1)[0]
            msg = self.rp[cmd]

            entity = None
            try:
                entity = await self.client.get_input_entity(message.text.split(' ', 2)[1])
            except:
                pass

            reply = await message.get_reply_message()

            try:
                reply = await self.client.get_entity(reply.sender_id)
            except:
                pass

            if not reply and not entity:
                return

            if reply and entity or not reply and entity:
                reply = entity

            sender = await self.client.get_entity(message.sender_id)

            await utils.answer(message, f'🦊 <a href="tg://user?id={sender.id}">{sender.first_name}</a> <b>{msg}</b> <a href="tg://user?id={reply.id}">{reply.first_name}</a>')
        except:
            pass
