#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://static.hikari.gay/secret_chat_icon.png
# meta banner: https://mods.hikariatama.ru/badges/secret_chat.jpg
# meta developer: @hikarimods
# requires: telethon_secret_chat
# scope: hikka_only
# scope: hikka_min 1.2.10

import io
import logging

from telethon.events import NewMessage
from telethon.tl.functions.channels import CreateChannelRequest
from telethon.tl.types import Message
from telethon.utils import get_display_name
from telethon_secret_chat import SecretChatManager

from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class SecretChatMod(loader.Module):
    """De-secrets secret chats"""

    strings = {"name": "SecretChat", "state": "👀 <b>SecretChat is now {}</b>"}

    def _get_chat_id(self, chat) -> int:
        cid = [chat.admin_id] + [chat.participant_id]
        cid.remove(self._tg_id)
        cid = cid[0]
        return cid

    async def _create_chat(self, chat):
        cid = self._get_chat_id(chat)

        decrypted_chat = None

        async for d in self._client.iter_dialogs():
            if d.title == f"secret-chat-with-{cid}":
                decrypted_chat = d.entity

        if not decrypted_chat:
            decrypted_chat = (
                await self._client(
                    CreateChannelRequest(
                        f"secret-chat-with-{cid}",
                        "SecretChat conversation with {}",
                        megagroup=True,
                    )
                )
            ).chats[0]

        @self._client.on(NewMessage(chats=[decrypted_chat.id]))
        async def secret_chat_processor(event):
            """secret_chat_processor"""
            await self._manager.send_secret_message(chat.id, event.text)
            await event.edit(f"<< {event.text}")

        self._chats[cid] = decrypted_chat

        self._manager = SecretChatManager(
            self._client,
            auto_accept=True,
            new_chat_created=self._new_chat,
        )
        self._manager.add_secret_event_handler(func=self._replier)
        self._chats = {}
        self._secret_chats = {}

    async def _replier(self, event):
        if not self.get("state", False):
            return

        e = event.decrypted_event
        user = self._secret_chats[event.message.chat_id]

        if e.message:
            await self._client.send_message(self._chats[user], f">> {e.message}")

        if e.file:
            try:
                m = await self._manager.download_secret_media(e)
                if m:
                    attrs = {}
                    f = io.BytesIO(m)
                    if "/" in (getattr(e.media, "mime_type", "") or ""):
                        f.name = "secret_media." + e.media.mime_type.split("/")[-1]

                    if getattr(e.media, "mime_type", None) == "audio/ogg":
                        attrs["voice_note"] = True

                    if getattr(e.media, "caption", False):
                        attrs["caption"] = e.media.caption

                    if "caption" not in attrs:
                        attrs["caption"] = ""

                    attrs["caption"] = ">> " + attrs["caption"]

                    await self._client.send_file(self._chats[user], f, **attrs)
            except Exception:
                await self._client.send_message(self._chats[user], ">>> [File]")

    async def _new_chat(self, chat, _: bool):
        if not self.get("state", False):
            return

        await self._create_chat(chat)
        user = self._get_chat_id(chat)
        self._secret_chats[chat.id] = user
        u = await self._client.get_entity(user)
        await self._client.send_message(
            self._chats[user],
            "㊙️ <b>New secret chat with <a"
            f' href="tg://user?id={user}">{get_display_name(u)}</a> started</b>',
        )

    async def on_unload(self):
        self._client.remove_event_handler(self._manager._secret_chat_event_loop)
        del self._manager
        for handler in self._client.list_event_handlers():
            if handler[0].__doc__ == "secret_chat_processor":
                self._client.remove_event_handler(handler)

    async def desecretcmd(self, message: Message):
        """Toggle secret chat handler"""
        current = self.get("state", False)
        new = not current
        self.set("state", new)
        await utils.answer(
            message, self.strings("state").format("on" if new else "off")
        )
