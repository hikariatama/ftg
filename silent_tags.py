# █ █ ▀ █▄▀ ▄▀█ █▀█ ▀    ▄▀█ ▀█▀ ▄▀█ █▀▄▀█ ▄▀█
# █▀█ █ █ █ █▀█ █▀▄ █ ▄  █▀█  █  █▀█ █ ▀ █ █▀█
#
#              © Copyright 2022
#
#          https://t.me/hikariatama
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://img.icons8.com/fluency/48/000000/witch.png
# meta developer: @hikariatama
# scope: hikka_only
# scope: hikka_min 1.0.18

from .. import loader, utils
import logging
import asyncio
from telethon.tl.types import Message
import time

logger = logging.getLogger(__name__)


@loader.tds
class SilentTagsMod(loader.Module):
    """Mutes tags and logs them"""

    strings = {
        "name": "SilentTags",
        "tagged": '<b>👋🏻 You were tagged in <a href="{}">{}</a> by <a href="tg://user?id={}">{}</a></b>\n<code>Message:</code>\n{}\n<b>Link: <a href="https://t.me/c/{}/{}">click</a></b>',
        "tag_mentioned": "<b>👾 Silent Tags are active</b>",
        "stags_status": "<b>👾 Silent Tags are {}</b>",
    }

    async def client_ready(self, client, db):
        self._client = client
        self._db = db
        self.stags = db.get("SilentTags", "stags", False)
        self._ratelimit = []
        self._fw_protect = {}
        self._fw_protect_limit = 5

        self.c, _ = await utils.asset_channel(
            self._client,
            "silent-tags",
            "🔇 Chat for silent tags",
            silent=True,
        )

    async def stagscmd(self, message: Message):
        """<on\\off> - Toggle notifications about tags"""
        args = utils.get_args_raw(message)

        if args not in ["on", "off"]:
            await utils.answer(
                message,
                self.strings("stags_status", message).format(
                    "active" if self.stags else "inactive"
                ),
            )
            return

        args = args == "on"
        self._db.set("SilentTags", "stags", args)
        self.stags = args
        self._ratelimit = []
        await utils.answer(
            message,
            self.strings("stags_status").format(
                "now on" if args else "now off", message
            ),
        )

    async def watcher(self, message: Message):
        try:
            if message.mentioned and self.stags:
                await self._client.send_read_acknowledge(
                    message.chat_id,
                    clear_mentions=True,
                )
                cid = utils.get_chat_id(message)

                if (
                    cid in self._fw_protect
                    and len(
                        list(filter(lambda x: x > time.time(), self._fw_protect[cid]))
                    )
                    > self._fw_protect_limit
                ):
                    return

                if message.is_private:
                    ctitle = "pm"
                else:
                    chat = await message.get_chat()
                    grouplink = (
                        f"https://t.me/{chat.username}"
                        if getattr(chat, "username", None) is not None
                        else ""
                    )
                    ctitle = chat.title

                if cid not in self._fw_protect:
                    self._fw_protect[cid] = []

                uid = message.from_id

                try:
                    user = await self._client.get_entity(message.from_id)
                    uname = user.first_name
                except Exception:
                    uname = "Unknown user"

                await self._client.send_message(
                    self.c,
                    self.strings("tagged").format(
                        grouplink,
                        ctitle,
                        uid,
                        uname,
                        message.raw_text,
                        cid,
                        message.id,
                    ),
                    link_preview=False,
                )
                self._fw_protect[cid] += [time.time() + 5 * 60]

                if cid not in self._ratelimit:
                    self._ratelimit += [cid]
                    ms = await utils.answer(message, self.strings("tag_mentioned"))
                    ms = ms[0] if isinstance(ms, list) else ms
                    await asyncio.sleep(5)
                    await ms.delete()
        except Exception:
            pass
