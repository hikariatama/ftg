#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://static.dan.tatar/userinfo_icon.png
# meta banner: https://mods.hikariatama.ru/badges/userinfo.jpg
# meta developer: @hikarimods
# scope: hikka_only
# scope: hikka_min 1.2.10

from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import Message

from .. import loader, utils


@loader.tds
class InfoMod(loader.Module):
    """Retrieve information about bot/user/chat"""

    strings = {
        "name": "Info",
        "loading": "🕐 <b>Processing entity...</b>",
        "not_chat": "🚫 <b>This is not a chat!</b>",
    }

    async def userinfocmd(self, message: Message):
        """Get object infomation"""
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()

        message = await utils.answer(message, self.strings("loading"))

        try:
            user_id = (
                (
                    (
                        await self._client.get_entity(
                            args if not args.isdigit() else int(args)
                        )
                    ).id
                )
                if args
                else reply.sender_id
            )
        except Exception:
            user_id = self._tg_id

        user = await self._client(GetFullUserRequest(user_id))

        user_ent = user.users[0]

        photo = await self._client.download_profile_photo(user_ent.id, bytes)

        user_info = (
            "<b>👤 User:</b>\n\n"
            f"<b>First name:</b> {user_ent.first_name or '🚫'}\n"
            f"<b>Last name:</b> {user_ent.last_name or '🚫'}\n"
            f"<b>Username:</b> @{user_ent.username or '🚫'}\n"
            f"<b>About:</b> \n<code>{user.full_user.about or '🚫'}</code>\n\n"
            f"<b>Shared Chats:</b> {user.full_user.common_chats_count}\n"
            f'<b><a href="tg://user?id={user_ent.id}">🌐 Permalink</a></b>\n\n'
            f"<b>ID:</b> <code>{user_ent.id}</code>\n"
        )

        if photo:
            await self._client.send_file(
                message.peer_id,
                photo,
                caption=user_info,
                link_preview=False,
                reply_to=reply.id if reply else None,
            )
            if message.out:
                await message.delete()
        else:
            await utils.answer(
                message,
                user_info,
                reply_to=reply.id if reply else None,
                link_preview=False,
            )
