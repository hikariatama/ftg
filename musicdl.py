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
        await utils.dnd(client, "@hikka_musicdl_bot", archive=True)

    async def mdlcmd(self, message: Message):
        """<name> - Download track"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings("args"))
            return

        message = await utils.answer(message, self.strings("loading"))

        async with self._client.conversation("@hikka_musicdl_bot") as conv:
            try:
                m = await conv.send_message(args)
                r = await conv.get_response()
                await m.delete()

                assert "Не получилось ничего найти" not in r.raw_text

                await r.click(0)
                await r.delete()
                r = await conv.get_response()

                assert r.document

                await self._client.send_file(
                    message.peer_id,
                    r.document,
                    caption=f"🎧 {utils.ascii_face()}",
                    reply_to=getattr(message, "reply_to_msg_id", None),
                )
                await r.delete()
                await message.delete()
            except Exception:
                await utils.answer(message, self.strings("404").format(args))
                return

        await self._client.delete_dialog("@hikka_musicdl_bot")
