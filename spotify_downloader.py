# █ █ ▀ █▄▀ ▄▀█ █▀█ ▀    ▄▀█ ▀█▀ ▄▀█ █▀▄▀█ ▄▀█
# █▀█ █ █ █ █▀█ █▀▄ █ ▄  █▀█  █  █▀█ █ ▀ █ █▀█
#
#              © Copyright 2022
#
#          https://t.me/hikariatama
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://img.icons8.com/plasticine/400/000000/spotify--v2.png
# meta developer: @hikariatama

from telethon.tl.types import Message

from .. import loader, utils


@loader.tds
class SpotifyDownloaderMod(loader.Module):
    """Download music from Spotify"""

    strings = {"name": "SpotifyDownloader"}

    async def client_ready(self, client, db):
        self._db = db
        self._client = client

    @loader.unrestricted
    async def sdcmd(self, message: Message):
        """<track> - search and download from Spotify"""
        args = utils.get_args_raw(message)
        if not args:
            return await utils.answer(message, "<b>No args.</b>")

        message = await utils.answer(message, "<b>Loading...</b>")
        music = await self._client.inline_query("spotifysavebot", args)
        for mus in music:
            if mus.result.type == "audio":
                await self._client.send_file(
                    message.peer_id,
                    mus.result.document,
                    reply_to=message.reply_to_msg_id,
                )
                return await message.delete()

        return await utils.answer(
            message, f"<b> Music named <code> {args} </code> not found. </b>"
        )
