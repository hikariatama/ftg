# █ █ ▀ █▄▀ ▄▀█ █▀█ ▀    ▄▀█ ▀█▀ ▄▀█ █▀▄▀█ ▄▀█
# █▀█ █ █ █ █▀█ █▀▄ █ ▄  █▀█  █  █▀█ █ ▀ █ █▀█
#
#              © Copyright 2022
#
#          https://t.me/hikariatama
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://img.icons8.com/external-justicon-lineal-color-justicon/512/000000/external-unlock-marketing-and-growth-justicon-lineal-color-justicon.png
# meta developer: @hikariatama
# scope: hikka_only
# scope: hikka_min 1.1.12

from .. import loader, utils
from telethon.tl.types import Message
import logging
from telethon_secret_chat import SecretChatManager
from telethon.utils import get_display_name
from telethon.tl.functions.channels import CreateChannelRequest
from telethon.events import NewMessage
import io

# requires: telethon_secret_chat

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
        async def secret_chat_processer(event):
            """secret_chat_processer"""
            await self._manager.send_secret_message(chat.id, event.text)
            await event.edit(f"<< {event.text}")

        self._chats[cid] = decrypted_chat

    async def client_ready(self, client, db):
        self._db = db
        self._client = client
        self._manager = SecretChatManager(
            client, auto_accept=True, new_chat_created=self._new_chat
        )
        self._manager.add_secret_event_handler(func=self._replier)
        self._chats = {}
        self._secret_chats = {}

    async def _replier(self, event):
        if not self.get("state", False):
            return

        # logger.info(event)
        e = event.decrypted_event
        user = self._secret_chats[event.message.chat_id]
        # logger.info(e)
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

            # send_secret_document
            # send_secret_audio
            # send_secret_video
            # send_secret_photo

    async def _new_chat(self, chat, created_by_me: bool):
        if not self.get("state", False):
            return

        await self._create_chat(chat)
        user = self._get_chat_id(chat)
        self._secret_chats[chat.id] = user
        u = await self._client.get_entity(user)
        await self._client.send_message(
            self._chats[user],
            f'㊙️ <b>New secret chat with <a href="tg://user?id={user}">{get_display_name(u)}</a> started</b>',
        )

    async def on_unload(self):
        self._client.remove_event_handler(self._manager._secret_chat_event_loop)
        del self._manager
        for handler in self._client.list_event_handlers():
            if handler[0].__doc__ == "secret_chat_processer":
                self._client.remove_event_handler(handler)

    async def desecretcmd(self, message: Message):
        """Toggle secret chat handler"""
        current = self.get("state", False)
        new = not current
        self.set("state", new)
        await utils.answer(
            message, self.strings("state").format("on" if new else "off")
        )
