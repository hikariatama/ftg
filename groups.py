# █ █ ▀ █▄▀ ▄▀█ █▀█ ▀    ▄▀█ ▀█▀ ▄▀█ █▀▄▀█ ▄▀█
# █▀█ █ █ █ █▀█ █▀▄ █ ▄  █▀█  █  █▀█ █ ▀ █ █▀█
#
#              © Copyright 2022
#
#          https://t.me/hikariatama
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://img.icons8.com/stickers/100/000000/id-verified.png
# meta developer: @hikariatama
# scope: inline

from .. import loader, utils, security  # noqa: F401

from telethon.tl.types import Message, User, PeerUser

import logging
from telethon.utils import get_display_name
from typing import Union

logger = logging.getLogger(__name__)


@loader.tds
class GroupsMod(loader.Module):
    """Control security groups"""

    strings = {
        "name": "Groups",
        "owner_list": "🤴 <b>Users in group </b><code>owner</code><b>:</b>\n\n{}",
        "sudo_list": "🤵‍♀️ <b>Users in group </b><code>sudo</code><b>:</b>\n\n{}",
        "support_list": "🙋‍♂️ <b>Users in group </b><code>support</code><b>:</b>\n\n{}",
        "no_owner": "🤴 <b>There is no users in group </b><code>owner</code>",
        "no_sudo": "🤵‍♀️ <b>There is no users in group </b><code>sudo</code>",
        "no_support": "🙋‍♂️ <b>There is no users in group </b><code>support</code>",
        "owner_added": '🤴 <b><a href="tg://user?id={}">{}</a> added to group </b><code>owner</code>',
        "sudo_added": '🤵‍♀️ <b><a href="tg://user?id={}">{}</a> added to group </b><code>sudo</code>',
        "support_added": '🙋‍♂️ <b><a href="tg://user?id={}">{}</a> added to group </b><code>support</code>',
        "owner_removed": '🤴 <b><a href="tg://user?id={}">{}</a> removed from group </b><code>owner</code>',
        "sudo_removed": '🤵‍♀️ <b><a href="tg://user?id={}">{}</a> removed from group </b><code>sudo</code>',
        "support_removed": '🙋‍♂️ <b><a href="tg://user?id={}">{}</a> removed from group </b><code>support</code>',
        "no_user": "🚫 <b>Specify user to permit</b>",
        "not_a_user": "🚫 <b>Specified entity is not a user</b>",
        "li": '⦿ <b><a href="tg://user?id={}">{}</a></b>',
        "warning": (
            '⚠️ <b>Please, confirm, that you want to add <a href="tg://user?id={}">{}</a> '
            'to group </b><code>{}</code><b>!\nThis action may reveal personal info and grant '
            'full or partial access to userbot to this user</b>'
        ),
        "cancel": "🚫 Cancel",
        "confirm": "👑 Confirm",
        "self": "🚫 <b>You can't promote/demote yourself!</b>",
        "restart": "<i>🔄 Restart may be required to commit changes</i>"
    }

    async def client_ready(self, client, db) -> Union[None, User]:
        self._db = db
        self._client = client
        self._me = (await client.get_me()).id
        if hasattr(self, "hikka"):
            raise loader.LoadError("You don't need this module, because it is included in your userbot")

    async def _resolve_user(self, message: Message):
        reply = await message.get_reply_message()
        args = utils.get_args_raw(message)

        if not args and not reply:
            await utils.answer(message, self.strings("no_user"))
            return

        user = None

        if args:
            try:
                if str(args).isdigit():
                    args = int(args)

                user = await self._client.get_entity(args)
            except Exception:
                pass

        if user is None:
            user = await self._client.get_entity(reply.sender_id)

        if not isinstance(user, (User, PeerUser)):
            await utils.answer(message, self.strings("not_a_user"))
            return

        if user.id == self._me:
            await utils.answer(message, self.strings("self"))
            return

        return user

    async def inline__close(
        self,
        call: "aigoram.types.CallbackQuery",  # noqa: F821
    ):
        await call.delete()

    async def _add_to_group(
        self,
        message: Union[Message, "aigoram.types.CallbackQuery"],  # noqa: F821
        group: str,
        confirmed: bool = False,
        user: int = None,
    ):
        if user is None:
            user = await self._resolve_user(message)
            if not user:
                return

        if isinstance(user, int):
            user = await self._client.get_entity(user)

        if self._is_hikka and not confirmed:
            await self.inline.form(
                self.strings("warning").format(
                    user.id, utils.escape_html(get_display_name(user)), group
                ),
                message=message,
                ttl=10 * 60,
                reply_markup=[
                    [
                        {
                            "text": self.strings("cancel"),
                            "callback": self.inline__close,
                        },
                        {
                            "text": self.strings("confirm"),
                            "callback": self._add_to_group,
                            "args": (group, True, user.id),
                        },
                    ]
                ],
            )
            return

        self._db.set(
            security.__name__,
            group,
            list(set(self._db.get(security.__name__, group, []) + [user.id])),
        )

        m = self.strings(f"{group}_added").format(
            user.id,
            utils.escape_html(get_display_name(user)),
        )

        if not self._is_hikka:
            m += f"\n\n{self.strings('restart')}"

        if isinstance(message, Message):
            await utils.answer(
                message,
                m,
            )
        else:
            await message.edit(m)

    async def _remove_from_group(self, message: Message, group: str):
        user = await self._resolve_user(message)
        if not user:
            return

        self._db.set(
            security.__name__,
            group,
            list(set(self._db.get(security.__name__, group, [])) - set([user.id])),
        )

        m = self.strings(f"{group}_removed").format(
            user.id,
            utils.escape_html(get_display_name(user)),
        )

        if not self._is_hikka:
            m += f"\n\n{self.strings('restart')}"

        await utils.answer(
            message,
            m
        )

    async def _list_group(self, message: Message, group: str):
        _resolved_users = []
        for user in self._db.get(security.__name__, group, []):
            try:
                _resolved_users += [await self._client.get_entity(user)]
            except Exception:
                pass

        if _resolved_users:
            await utils.answer(
                message,
                self.strings(f"{group}_list").format(
                    "\n".join(
                        [
                            self.strings("li").format(
                                i.id, utils.escape_html(get_display_name(i))
                            )
                            for i in _resolved_users
                        ]
                    )
                ),
            )
        else:
            await utils.answer(message, self.strings(f"no_{group}"))

    async def sudoaddcmd(self, message: Message):
        """<user> - Add user to `sudo`"""
        await self._add_to_group(message, "sudo")

    async def owneraddcmd(self, message: Message):
        """<user> - Add user to `owner`"""
        await self._add_to_group(message, "owner")

    async def supportaddcmd(self, message: Message):
        """<user> - Add user to `support`"""
        await self._add_to_group(message, "support")

    async def sudormcmd(self, message: Message):
        """<user> - Remove user from `sudo`"""
        await self._remove_from_group(message, "sudo")

    async def ownerrmcmd(self, message: Message):
        """<user> - Remove user from `owner`"""
        await self._remove_from_group(message, "owner")

    async def supportrmcmd(self, message: Message):
        """<user> - Remove user from `support`"""
        await self._remove_from_group(message, "support")

    async def sudolistcmd(self, message: Message):
        """List users in `sudo`"""
        await self._list_group(message, "sudo")

    async def ownerlistcmd(self, message: Message):
        """List users in `owner`"""
        await self._list_group(message, "owner")

    async def supportlistcmd(self, message: Message):
        """List users in `support`"""
        await self._list_group(message, "support")
