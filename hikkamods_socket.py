# █ █ ▀ █▄▀ ▄▀█ █▀█ ▀    ▄▀█ ▀█▀ ▄▀█ █▀▄▀█ ▄▀█
# █▀█ █ █ █ █▀█ █▀▄ █ ▄  █▀█  █  █▀█ █ ▀ █ █▀█
#
#              © Copyright 2022
#
#          https://t.me/hikariatama
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta developer: @hikariatama
# requires: rsa base64

import asyncio
from .. import loader
from telethon.tl.types import Message
import logging
import rsa
import base64

logger = logging.getLogger(__name__)

pubkey = rsa.PublicKey(
    7110455561671499155469672749235101198284219627796886527432331759773809536504953770286294224729310191037878347906574131955439231159825047868272932664151403,
    65537,
)


@loader.tds
class HikkaModsSocketMod(loader.Module):
    """Gives @hikkamods_bot a right to download modules from official modules aggregator"""

    strings = {"name": "HikkaModsSocket"}

    async def on_unload(self):
        asyncio.ensure_future(
            self._client.inline_query("@hikkamods_bot", "#statunload:hikkamods_socket")
        )

    async def stats_task(self):
        await asyncio.sleep(60)
        await self._client.inline_query(
            "@hikkamods_bot",
            f"#statload:{','.join(list(set(self.allmodules._hikari_stats)))}",
        )
        delattr(self.allmodules, "_hikari_stats")
        delattr(self.allmodules, "_hikari_stats_task")

    async def client_ready(self, client, db):
        self._db = db
        self._client = client

        if not hasattr(self.allmodules, "_hikari_stats"):
            self.allmodules._hikari_stats = []

        self.allmodules._hikari_stats += ["hikkamods_socket"]

        if not hasattr(self.allmodules, "_hikari_stats_task"):
            self.allmodules._hikari_stats_task = asyncio.ensure_future(
                self.stats_task()
            )

    async def watcher(self, message: Message):
        if (
            not isinstance(message, Message)
            or message.sender_id != 5519484330
            or not message.raw_text.startswith("#install")
        ):
            return

        await message.delete()

        fileref = message.raw_text.split("#install:")[1].strip().splitlines()[0].strip()
        sig = base64.b64decode(message.raw_text.splitlines()[1].strip().encode())
        try:
            rsa.verify(rsa.compute_hash(fileref.encode("utf-8"), "SHA-1"), sig, pubkey)
        except rsa.pkcs1.VerificationError:
            logger.error(f"Got message with non-verified signature ({fileref=})")
            return

        await self.lookup("loader").download_and_install(
            f"https://heta.hikariatama.ru/{fileref}",
            None,
        )

        if self.lookup("loader")._fully_loaded:
            self.lookup("loader")._update_modules_in_db()

        if any(
            link == f"https://heta.hikariatama.ru/{fileref}"
            for link in self.lookup("loader").get("loaded_modules", {}).values()
        ):
            await message.respond(
                f"/verify_load {message.raw_text.splitlines()[2].strip()}"
            )
        else:
            await message.respond(
                f"/verify_fload {message.raw_text.splitlines()[2].strip()}"
            )
