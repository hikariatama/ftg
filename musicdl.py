#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# scope: hikka_min 1.2.10

# meta pic: https://img.icons8.com/color/344/earbud-headphones.png
# meta developer: @hikarimods

from .. import loader, utils
from telethon.tl.types import Message


@loader.tds
class MusicDLMod(loader.Module):
    """Download music"""

    strings = {
        "name": "MusicDL",
        "args": "🚫 <b>Arguments not specified</b>",
        "loading": "🔍 <b>Loading...</b>",
        "404": "🚫 <b>Music </b><code>{}</code><b> not found</b>",
    }

    async def client_ready(self, client, db):
        self.musicdl = await self.import_lib(
            "https://libs.hikariatama.ru/musicdl.py",
            suspend_on_error=True,
        )

    async def mdlcmd(self, message: Message):
        """<name> - Download track"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings("args"))
            return

        message = await utils.answer(message, self.strings("loading"))
        result = await self.musicdl.dl(args, only_document=True)

        if result:
            await self._client.send_file(
                message.peer_id,
                result,
                caption=f"🎧 {utils.ascii_face()}",
                reply_to=getattr(message, "reply_to_msg_id", None),
            )
            if message.out:
                await message.delete()
        else:
            await utils.answer(message, self.strings("404").format(args))
