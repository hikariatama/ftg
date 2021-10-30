"""
    Copyright 2021 t.me/innocoffee
    Licensed under the Apache License, Version 2.0
    
    Author is not responsible for any consequencies caused by using this
    software or any of its parts. If you have any questions or wishes, feel
    free to contact Dan by sending pm to @innocoffee_alt.
"""

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
            print('txt', 'lc' in txt)
            if "lc" not in txt:
                self.allmodules.last_command = func
            return txt, func

        self.allmodules.dispatch = _disp_wrap

    async def lccmd(self, message):
        await self.allmodules.last_command(message)
