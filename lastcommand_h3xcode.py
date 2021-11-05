"""
    Copyright 2021 t.me/innocoffee
    Licensed under the Apache License, Version 2.0
    
    Author is not responsible for any consequencies caused by using this
    software or any of its parts. If you have any questions or wishes, feel
    free to contact Dan by sending pm to @innocoffee_alt.
"""

#<3 title: LastCommand h3xcode
#<3 pic: https://img.icons8.com/fluency/48/000000/last-12-hours.png
#<3 desc: Выполнить предыдущую команду, версия @h3xcode

from .. import loader, utils
import asyncio
import os


@loader.tds
class LastCommandMod(loader.Module):
    """Execute last command"""
    strings = {'name': 'LastCommand'}

    async def client_ready(self, client, db):
        orig_dispatch = self.allmodules.dispatch

        def _disp_wrap(command):
            txt, func = orig_dispatch(command)
            if "lc" not in txt:
                self.allmodules.last_command = func
            return txt, func

        self.allmodules.dispatch = _disp_wrap

    async def lccmd(self, message):
        await self.allmodules.last_command(message)
