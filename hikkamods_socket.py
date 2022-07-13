#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# scope: hikka_min 1.2.10

# meta developer: @hikariatama
# requires: rsa base64

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
