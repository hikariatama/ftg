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
import io
import json

@loader.tds
class RPMod(loader.Module):
    """RPMod от Innomods"""
    strings = {
        'name': 'RPMod',
        'args': '🦊 <b>Incorrect args</b>',
        'success': '🦊 <b>Success</b>',
        'rp_on': '🦊 <b>RPM on</b>',
        'rp_off': '🦊 <b>RPM off</b>',
        'rplist': '🦊 <b>Current RP commands</b>\n\n{}',
        'backup_caption': '🦊 <b>My RP commands. Restore with </b><code>.rprestore</code>', 
        'no_file': '🦊 <b>Reply to file</b>',
        'restored': '🦊 <b>RP Commands restored. See them with </b><code>.rplist</code>'
    }

    async def client_ready(self, client, db):
        self.db = db
        self.client = client
        self.rp = db.get('RPMod', 'rp', {})
        self.chats = db.get('RPMod', 'active', [])

    async def rpcmd(self, message):
        """<command> <message> - Add RP Command. If message unspecified, remove command"""
        args = utils.get_args_raw(message)
        try:
            command = args.split(' ', 1)[0]
            msg = args.split(' ', 1)[1]
        except:
            if not args or command not in self.rp:
                await utils.answer(message, self.strings('args', message))
            else:
                del self.rp[command]
                self.db.set('RPMod', 'rp', self.rp)
                await utils.answer(message, self.strings('success', message))
            return
        self.rp[command] = msg
        self.db.set('RPMod', 'rp', self.rp)
        await utils.answer(message, self.strings('success', message))


    async def rptogglecmd(self, message):
        """Toggle RP Mode in current chat"""
        cid = str(utils.get_chat_id(message))
        if cid in self.chats:
            self.chats.remove(cid)
            await utils.answer(message, self.strings('rp_off', message))
        else:
            self.chats.append(cid)
            await utils.answer(message, self.strings('rp_on', message))
        self.db.set('RPMod', 'active', self.chats)

    @loader.unrestricted
    async def rplistcmd(self, message):
        """List RP Commands"""
        await utils.answer(message, self.strings('rplist').format('\n'.join([f"    🇨🇭 {command} - {msg}" for command, msg in self.rp.items()])))

    async def rpbackupcmd(self, message):
        """Backup RP Commands to file"""
        file = io.BytesIO(json.dumps(self.rp).encode('utf-8'))
        file.name = 'rp-backup.json'
        await self.client.send_file(utils.get_chat_id(message), file, caption=self.strings('backup_caption'))
        await message.delete()

    async def rprestorecmd(self, message):
        """Restore RP Commands from file"""
        reply = await message.get_reply_message()
        if not reply or not reply.media:
            await utils.answer(message, self.strings('no_file'))
            return

        file = (await self.client.download_file(reply.media)).decode('utf-8')
        self.rp = json.loads(file)
        self.db.set('RPMod', 'rp', self.rp)
        await utils.answer(message, self.strings('restored'))

    async def rpchatscmd(self, message):
        """List chats, where RPM is active"""
        res = f"🦊 <b>RPM is active in {len(self.chats)} chats:</b>\n\n"
        for chat in self.chats:
            chat_obj = await self.client.get_entity(int(chat))
            if getattr(chat_obj, 'title', False):
                chat_name = chat_obj.title
            else:
                chat_name = chat_obj.first_name

            res += "    🇯🇵 " + chat_name + "\n"

        await utils.answer(message, res)

    
    async def watcher(self, message):
        try:
            cid = str(utils.get_chat_id(message))
            if cid not in self.chats:
                return

            if message.text.split(' ', 1)[0].lower() not in self.rp:
                return

            cmd = message.text.split(' ', 1)[0].lower()
            msg = self.rp[cmd]

            entity = None
            try:
                entity = await self.client.get_entity(message.text.split(' ', 2)[1])
            except:
                pass

            reply = await message.get_reply_message()

            try:
                reply = await self.client.get_entity(reply.sender_id)
            except:
                pass

            if not reply and not entity:
                return

            if reply and entity or not reply:
                reply = entity

            sender = await self.client.get_entity(message.sender_id)

            await utils.answer(message, f'🦊 <a href="tg://user?id={sender.id}">{sender.first_name}</a> <b>{msg}</b> <a href="tg://user?id={reply.id}">{reply.first_name}</a>')
        except:
            return
