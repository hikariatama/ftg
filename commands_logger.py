"""
    Copyright 2021 t.me/innocoffee
    Licensed under the Apache License, Version 2.0
    
    Author is not responsible for any consequencies caused by using this
    software or any of its parts. If you have any questions or wishes, feel
    free to contact Dan by sending pm to @innocoffee_alt.
"""

#<3 title: CommandsLogger
#<3 pic: https://img.icons8.com/fluency/50/000000/event-log.png
#<3 desc: Логирование выполненных команд

from .. import loader, utils, main
from telethon.tl.functions.channels import CreateChannelRequest
import logging
import copy
from telethon.events import NewMessage
import telethon.utils as tutils

logger = logging.getLogger(__name__)

@loader.tds
class CommandsLoggerMod(loader.Module):
    """Log any evaluated commands\nOnly supported by GeekTG v2.0.2+"""

    strings = {
        "name": "CommandsLogger"
    }

    async def find_db(self):
        async for d in self.client.iter_dialogs():
            if d.title == "geektg-log":
                return d.entity

        return (await self.client(CreateChannelRequest("geektg-log", f"Commands will appear there", megagroup=True))).chats[0]


    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        try:
            self.geektg_ver = main.__version__
        except Exception:
            raise Exception('This module is supported only by GeekTG')

        if self.geektg_ver < (2, 0, 2):
            raise Exception('Module is not supported in your version of GeekTG. Please, update')

        self.log_channel = await self.find_db()
        self.prefix = utils.escape_html((self.db.get(main.__name__, "command_prefix", False) or ".")[0])
        loader.mods = self.allmodules.modules

        logger.warning('Logging installed')

    async def process_log(self, message):
        by = f"\n<b>By: <a href=\"tg://user?id={message.sender.id}\">{tutils.get_display_name(message.sender)}</a></b>" if not message.out else ""
        await self.client.send_message(self.log_channel, f"<code>{self.prefix}{message.raw_text}</code>{by}")


