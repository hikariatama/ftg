"""
    Copyright 2021 t.me/innocoffee
    Licensed under the Apache License, Version 2.0
    
    Author is not responsible for any consequencies caused by using this
    software or any of its parts. If you have any questions or wishes, feel
    free to contact Dan by sending pm to @innocoffee_alt.
"""

# <3 title: Keyword
# <3 pic: https://img.icons8.com/fluency/48/000000/macbook-chat.png
# <3 desc: Отвечать на определенные сообщения заданной фразой

from .. import loader, utils
import logging

logger = logging.getLogger(__name__)

@loader.tds
class KeywordMod(loader.Module):
    """Keyword"""
    strings = {
        'name': 'Keyword',
        'args': '🦊 <b>Args are incorrect</b>',
        'kw_404': '🦊 <b>Keyword "{}" not found in db</b>', 
        'kw_added': '🦊 <b>New keyword:\nTrigger: {}\nMessage: {}\n{}{}{}</b>',
        'kw_removed': '🦊 <b>Keyword "{}" removed</b>', 
        'bl_added': '🦊 <b>This chat is now blacklisted for Keywords</b>',
        'bl_removed': '🦊 <b>This chat is now whitelisted for Keywords</b>',
        'sent': '🦊 <b>[Keywords]: Sent message to {}, triggered by {}:\n{}</b>',
        'kwords': '🦊 <b>Current keywords:\n{}</b>'
    }

    async def client_ready(self, client, db):
        self.db = db
        self.client = client
        self.keywords = db.get('Keyword', 'keywords', {})
        self.bl = db.get('Keyword', 'bl', [])

    async def kwordcmd(self, message):
        """<keyword | could be in qutoes | & for multiple words that should be in msg> <message | empty to remove keyword> [-r for full match] [-m for autoreading msg] [-l to log in pm]"""
        args = utils.get_args_raw(message)
        kw, ph, restrict, ar, l = "", "", False, False, False
        if '-r' in args:
            restrict = True
            args = args.replace(' -r', '').replace('-r', '')

        if '-m' in args:
            ar = True
            args = args.replace(' -m', '').replace('-m', '')

        if '-l' in args:
            l = True
            args = args.replace(' -l', '').replace('-l', '')

        if args[0] == "'":
            kw = args[1:args.find("'", 1)]
            args = args[args.find("'", 1) + 1:]
        elif args[0] == '"':
            kw = args[1:args.find('"', 1)]
            args = args[args.find('"', 1) + 1:]
        else:
            kw = args.split()[0]
            try:
                args = args.split(maxsplit=1)[1]
            except:
                args = ""

        ph = args
        if not ph:
            if kw in self.keywords:
                del self.keywords[kw]
                self.db.set('Keyword', 'keywords', self.keywords)
                return await utils.answer(message, self.strings('kw_removed').format(kw))
            else:
                return await utils.answer(message, self.strings('kw_404').format(kw))
        else:
            ph = ph.strip()
            kw = kw.strip()
            self.keywords[kw] = [ph, restrict, ar, l]
            self.db.set('Keyword', 'keywords', self.keywords)
            return await utils.answer(message, self.strings('kw_added').format(kw, ph, ('Restrict: yes\n' if restrict else ''), ('Auto-read: yes\n' if ar else ''), ('Log: yes' if l else '')))


    async def kwordscmd(self, message):
        """List current kwords"""
        res = ""
        for kw, ph in self.keywords.items():
            res += kw + '\nMessage: ' + ph[0] + '\n' + ('Restrict: yes\n' if ph[1] else '') + ('Auto-read: yes\n' if ph[1] else '') + ('Log: yes' if ph[1] else '')
            if res[-1] != '\n':
                res += '\n'

        await utils.answer(message, self.strings('kwords').format(res))


    async def kwblcmd(self, message):
        """Blacklist chat from answering keywords"""
        cid = utils.get_chat_id(message)
        if cid not in self.bl:
            self.bl.append(cid)
            self.db.set('Keyword', 'bl', self.bl)
            return await utils.answer(message, self.strings('bl_added'))
        else:
            self.bl.remove(cid)
            self.db.set('Keyword', 'bl', self.bl)
            return await utils.answer(message, self.strings('bl_removed'))

    async def watcher(self, message):
        try:
            # logger.debug(message)
            if message.out: return

            cid = utils.get_chat_id(message)
            if cid in self.bl: return

            for kw, ph in self.keywords.items():
                kws = [_.strip() for _ in ([kw] if '&' not in kw else kw.split('&'))]
                trigger = False
                for k in kws:
                    if k in message.text:
                        trigger = True
                        if not ph[1]:
                            break
                    elif k not in message.text and ph[1]:
                        trigger = False
                        break

                if not trigger:
                    continue

                if ph[2]:
                    await self.client.send_read_acknowledge(cid, clear_mentions=True)

                if ph[3]:
                    chat = await message.get_chat()
                    ch = (message.first_name if getattr(message, 'first_name', None) is not None else '')
                    if not ch:
                        ch = (chat.title if getattr(message, 'title', None) is not None else '')
                    await self.client.send_message('me', self.strings('sent').format(ch, kw, ph[0]))

                return await utils.answer(message, ph[0])
        except Exception as e:
            logger.debug(e)
