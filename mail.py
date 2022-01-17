"""
    Copyright 2021 t.me/hikariakami
    Licensed under the Apache License, Version 2.0
    
    Author is not responsible for any consequencies caused by using this
    software or any of its parts. If you have any questions or wishes, feel
    free to contact Dan by sending pm to @hikari_alt.
"""

#<3 title: Mail
#<3 pic: https://img.icons8.com/fluency/48/000000/mail.png
#<3 desc: Клиент электронной почты (уведомления)

from .. import loader, utils
import asyncio
import imaplib
import email
import json
import re
import logging

logger = logging.getLogger(__name__)


@loader.tds
class MailMod(loader.Module):
    strings = {
        "name": "Mail"
    }

    async def parser(self):
        imap = imaplib.IMAP4_SSL('imap.mail.ru', 993)
        imap.login(self.config['mail'], self.config['password'])
        imap.select('inbox')
        while True:
            result, data = imap.uid('search', None, "ALL")
            n = data[0].decode().count(' ') + 1
            if n == self.cached:
                await asyncio.sleep(10)
                continue

            self.cached = n
            self.db.set(__name__, 'cached', self.cached)

            latest_email_uid = data[0].split()[-1]
            result, data = imap.uid('fetch', latest_email_uid, '(RFC822)')
            raw_email = data[0][1]
            email_message = email.message_from_string(raw_email.decode())
            def get_text(msg):
                try:
                    t = '\n'.join([_.get_payload() for _ in msg.get_payload() if _.get_content_maintype() == 'text'])
                except AttributeError:
                    t = msg.get_payload()
                t = t.replace('<div>', '\n')
                t = t.replace('</div>', '')
                t = re.sub(r'<br.*?>', '\n', t)
                t = t.replace('<', '&lt;').replace('>', '&gt;')
                return t

            _from, _text = email.utils.parseaddr(email_message['From'])[1], get_text(email_message)
            _subject = email.utils.parseaddr(email_message['Subject'])[1]
            logger.info(f'New mail from {_from} ({_subject}):\n\n{_text}')
            await self.client.send_message('@userbot_notifies_bot', f'✉️ <b>New message</b>\n<b>From:</b> <code>{_from}</code>\n<b>Subject: </b><code>{_subject}</code>\n\n{_text}', parse_mode=None)
            await asyncio.sleep(10)


    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        self.cached = db.get(__name__, 'cached', 0)

        asyncio.ensure_future(self.parser())

    def __init__(self):
        self.config = loader.ModuleConfig("mail", 'elusloodus@mail.ru', lambda: "E-mail",
                                            "password", '', lambda: "Password for external apps")

