__version__ = (1, 0, 4)

#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://img.icons8.com/external-sketchy-juicy-fish/480/000000/external-anonymous-cryptography-sketchy-sketchy-juicy-fish.png
# meta banner: https://mods.hikariatama.ru/badges/spoilers.jpg
# meta developer: @hikarimods
# scope: inline
# scope: hikka_only
# scope: hikka_min 1.3.3

from telethon.utils import get_display_name
from telethon.utils import resolve_inline_message_id
import logging

from .. import loader, utils
from ..inline.types import InlineCall, InlineQuery

logger = logging.getLogger(__name__)


@loader.tds
class SpoilersMod(loader.Module):
    """Create spoilers, that can be accessed only by certain users"""

    _cache = {}
    _msg_cache = {}

    strings = {
        "name": "Spoilers",
        "only_he_can_open": "ℹ Only (s)he will be able to open it",
        "message": (
            '🫦 <b>Hidden message for <a href="tg://user?id={}">{}</a></b>\n<i>You can'
            " open this message only once!</i>"
        ),
        "user_not_specified": (
            "🫦 <b>Hidden message for you!</b>\n<i>You can"
            " open this message only once!</i>"
        ),
        "not4u": "🫦 I won't whisper you",
        "open": "👀 Open",
        "in_the_end": "Send spoiler to user in reply",
        "broken": "🫦 Cats have eaten this whisper. Do not whisper in pm anymore.",
    }

    strings_ru = {
        "only_he_can_open": "ℹ Только он(-а) сможет открыть его",
        "message": (
            '🫦 <b>Шепот для <a href="tg://user?id={}">{}</a></b>\n<i>Сообщение можно'
            " открыть только один раз!</i>"
        ),
        "user_not_specified": (
            "🫦 <b>Шепот для тебя!</b>\n<i>Сообщение можно открыть только один раз!"
            "</i>"
        ),
        "not4u": "🫦 Я не буду тебе шептать",
        "open": "👀 Открыть",
        "in_the_end": "Отправь шепот пользователю в ответе",
        "_ihandle_doc_hide": "Создать спойлер",
        "_cls_doc": (
            "Создает спойлеры, которые доступны только определенным пользователям"
        ),
        "broken": "🫦 Коты съели этот шепот. Не шепчите в личных сообщениях.",
    }

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
                text = " ".join(text.split(" ")[1:])

        id_ = utils.rand(16)
        self._cache[id_] = text

        return {
            "title": for_user,
            "description": self.strings("only_he_can_open"),
            "message": (
                self.strings("message").format(
                    for_user_id,
                    utils.escape_html(get_display_name(user)),
                )
                if user
                else self.strings("user_not_specified").format(id_)
            ),
            "thumb": "https://img.icons8.com/color/48/000000/anonymous-mask.png",
            "reply_markup": {
                "text": self.strings("open"),
                "callback": self._handler,
                "args": (text, for_user_id, id_),
                "disable_security": True,
            },
        }

    async def _handler(self, call: InlineCall, text: str, for_user: int, id_: str):
        """Process button presses"""
        if for_user is None:
            if id_ not in self._msg_cache:
                message_id, peer, _, _ = resolve_inline_message_id(call.inline_message_id)
                msg = (await self._client.get_messages(peer, ids=[message_id]))[0]
                if msg is None:
                    await call.answer(self.strings("broken"))
                    self._msg_cache[id_] = None
                    return

                msg = await msg.get_reply_message()
                if msg is None:
                    await call.answer(self.strings("broken"))
                    self._msg_cache[id_] = None
                    return
            else:
                msg = self._msg_cache[id_]
                if msg is None:
                    await call.answer(self.strings("broken"))
                    return
            
            for_user = msg.sender_id
            self._msg_cache[id_] = msg

        if call.from_user.id not in {
            for_user,
            self._tg_id,
        }:
            await call.answer(self.strings("not4u"))
            return

        await call.answer(text, show_alert=True)

        if call.from_user.id != self._tg_id:
            message_id, peer, _, _ = resolve_inline_message_id(call.inline_message_id)
            await self._client.delete_messages(peer, [message_id])
