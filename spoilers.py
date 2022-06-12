__version__ = (1, 0, 4)

# █ █ ▀ █▄▀ ▄▀█ █▀█ ▀    ▄▀█ ▀█▀ ▄▀█ █▀▄▀█ ▄▀█
# █▀█ █ █ █ █▀█ █▀▄ █ ▄  █▀█  █  █▀█ █ ▀ █ █▀█
#
#              © Copyright 2022
#
#          https://t.me/hikariatama
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://img.icons8.com/external-sketchy-juicy-fish/480/000000/external-anonymous-cryptography-sketchy-sketchy-juicy-fish.png
# meta developer: @hikarimods
# scope: inline
# scope: hikka_only
# scope: hikka_min 1.1.12

import logging

from telethon.utils import get_display_name

from .. import loader, utils
from ..inline.types import InlineCall, InlineQuery

logger = logging.getLogger(__name__)


@loader.tds
class SpoilersMod(loader.Module):
    """Create spoilers, that can be accessed only by certain users"""

    strings = {
        "name": "Spoilers",
        "only_he_can_open": "ℹ Only (s)he will be able to open it",
        "message": '🙈 <b>Hidden message for <a href="tg://user?id={}">{}</a></b>\n<i>You can open this message only once!</i>',
        "user_not_specified": "🚫 <b>User not specified</b>",
        "not4u": "This button is not for you",
        "seen": "🕔 <b>Seen</b>",
        "open": "👀 Open",
        "in_the_end": "Specify username as first argument",
    }

    strings_ru = {
        "only_he_can_open": "ℹ Только он(-а) сможет открыть его",
        "message": '🙈 <b>Шепот для <a href="tg://user?id={}">{}</a></b>\n<i>Сообщение можно открыть только один раз!</i>',
        "user_not_specified": "🚫 <b>Пользователь не указан</b>",
        "not4u": "Эта кнопка не для тебя",
        "seen": "🕔 <b>Просмотрено</b>",
        "open": "👀 Открыть",
        "in_the_end": "Укажи @username или ID первым аргументом",
        "_ihandle_doc_hide": "Создать спойлер",
        "_cls_doc": "Создает спойлеры, которые доступны только определенным пользователям",
    }

    async def client_ready(self, client, db):
        self._db = db
        self._client = client

    async def hide_inline_handler(self, query: InlineQuery):
        """Create new hidden message"""
        text = query.args
        for_user = self.strings("in_the_end")
        for_user_id = None
        user = None
        if len(text.split()) > 1:
            try:
                possible_entity = text.split()[0]

                if possible_entity.isdigit():
                    possible_entity = int(possible_entity)

                user = await self._client.get_entity(possible_entity)
            except Exception:
                pass
            else:
                for_user = "Hidden message for " + get_display_name(user)
                for_user_id = user.id

        return {
            "title": for_user,
            "description": self.strings("only_he_can_open"),
            "message": (
                self.strings("message").format(
                    for_user_id,
                    utils.escape_html(get_display_name(user)),
                )
                if user
                else self.strings("user_not_specified")
            ),
            "thumb": "https://img.icons8.com/color/48/000000/anonymous-mask.png",
            "reply_markup": {
                "text": self.strings("open"),
                "callback": self._handler,
                "args": (" ".join(text.split(" ")[1:]), for_user_id),
                "always_allow": [for_user_id],
            }
            if for_user_id
            else {},
        }

    async def _handler(self, call: InlineCall, text: str, for_user: int):
        """Process button presses"""
        if call.from_user.id not in {
            for_user,
            self._tg_id,
        }:
            await call.answer(self.strings("not4u"))
            return

        await call.answer(text, show_alert=True)

        if call.from_user.id != self._tg_id:
            await call.edit(self.strings("seen"))
