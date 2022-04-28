# █ █ ▀ █▄▀ ▄▀█ █▀█ ▀    ▄▀█ ▀█▀ ▄▀█ █▀▄▀█ ▄▀█
# █▀█ █ █ █ █▀█ █▀▄ █ ▄  █▀█  █  █▀█ █ ▀ █ █▀█
#
#              © Copyright 2022
#
#          https://t.me/hikariatama
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://img.icons8.com/fluency/48/000000/edit-message.png
# meta developer: @hikariatama
# scope: hikka_only

from .. import loader, utils
from telethon.tl.types import Message, User, Chat
import logging
import time
from telethon.utils import get_display_name

logger = logging.getLogger(__name__)


@loader.tds
class ActivistsMod(loader.Module):
    """Looks for the most active users in chat"""

    strings = {
        "name": "Activists",
        "searching": "🔎 <b>Looking for the most active users in chat...\nThis might take a while.</b>",
        "user": '👤 {}. <a href="{}">{}</a>: {} messages',
        "active": "👾 <b>The most active users in this chat:</b>\n\n{}\n<i>Request took: {}s</i>",
    }

    async def client_ready(self, client, db):
        self._db = db
        self._client = client

    async def check_admin(self, chat: int or Chat, user_id: int or User) -> bool:
        try:
            return (await self._client.get_permissions(chat, user_id)).is_admin
        except Exception:
            return False

    async def activistscmd(self, message: Message):
        """[quantity] [-m <int>] - Find top active users in chat"""
        args = utils.get_args_raw(message)
        limit = None
        if "-m" in args:
            limit = int(
                "".join([lim for lim in args[args.find("-m") + 2 :] if lim.isdigit()])
            )
            args = args[: args.find("-m")].strip()

        quantity = int(args) if args.isdigit() else 15

        message = await utils.answer(message, self.strings("searching"))
        message = message[0] if isinstance(message, (list, tuple, set)) else message

        st = time.perf_counter()

        temp = {}
        async for msg in self._client.iter_messages(message.peer_id, limit=limit):
            user = getattr(msg, "sender_id", False)
            if not user:
                continue

            if user not in temp:
                temp[user] = 0

            temp[user] += 1

        stats = [
            user[0]
            for user in list(sorted(list(temp.items()), key=lambda x: x[1], reverse=True))
        ]

        top_users = []
        for u in stats:
            if len(top_users) >= quantity:
                break

            if not await self.check_admin(message.peer_id, u):
                top_users += [(await self._client.get_entity(u), u)]

        top_users_formatted = [
            self.strings("user").format(
                i + 1, utils.get_link(user[0]), get_display_name(user[0]), temp[user[1]]
            )
            for i, user in enumerate(top_users)
        ]

        await utils.answer(
            message,
            self.strings("active").format(
                "\n".join(top_users_formatted), round(time.perf_counter() - st, 2)
            ),
        )
