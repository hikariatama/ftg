# █ █ ▀ █▄▀ ▄▀█ █▀█ ▀    ▄▀█ ▀█▀ ▄▀█ █▀▄▀█ ▄▀█
# █▀█ █ █ █ █▀█ █▀▄ █ ▄  █▀█  █  █▀█ █ ▀ █ █▀█
#
#              © Copyright 2022
#
#          https://t.me/hikariatama
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://img.icons8.com/fluency/48/000000/last-12-hours.png
# meta developer: @hikariatama

from .. import loader
from telethon.tl.types import Message


@loader.tds
class LastCommandMod(loader.Module):
    """Execute last command"""

    strings = {"name": "LastCommand"}

    async def client_ready(self, client, db):
        orig_dispatch = self.allmodules.dispatch

        def _disp_wrap(command):
            txt, func = orig_dispatch(command)
            if "lc" not in txt:
                self.allmodules.last_command = func
            return txt, func

        self.allmodules.dispatch = _disp_wrap

    async def lccmd(self, message: Message):
        """Execute last command"""
        await self.allmodules.last_command(message)
