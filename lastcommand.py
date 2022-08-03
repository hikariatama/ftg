#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://static.hikari.gay/lastcommand_icon.png
# meta banner: https://mods.hikariatama.ru/badges/lastcommand.jpg
# meta developer: @hikarimods
# scope: hikka_only
# scope: hikka_min 1.2.10

from telethon.tl.types import Message

from .. import loader


@loader.tds
class LastCommandMod(loader.Module):
    """Execute last command"""

    strings = {"name": "LastCommand"}

    async def client_ready(self):
        orig_dispatch = self.allmodules.dispatch

        def _disp_wrap(command: callable) -> tuple:
            txt, func = orig_dispatch(command)

            if "lc" not in txt:
                self.allmodules.last_command = func

            return txt, func

        self.allmodules.dispatch = _disp_wrap

    async def lccmd(self, message: Message):
        """Execute last command"""
        await self.allmodules.last_command(message)
