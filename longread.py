# scope: hikka_min 1.2.10
__version__ = (1, 0, 2)

#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://img.icons8.com/external-wanicon-lineal-color-wanicon/512/000000/external-read-free-time-wanicon-lineal-color-wanicon.png
# meta developer: @hikarimods
# scope: inline
# scope: hikka_only

from .. import loader, utils
from ..inline.types import InlineCall, InlineQuery
from telethon.tl.types import Message


@loader.tds
class LongReadMod(loader.Module):
    """Pack longreads under button spoilers"""

    strings = {
        "name": "LongRead",
        "no_text": "🚫 <b>Please, specify text to hide</b>",
        "longread": (
            "🗄 <b>This is long read</b>\n<i>Click button to show text!\nThis button is"
            " active within 6 hours</i>"
        ),
    }

    strings_ru = {
        "no_text": "🚫 <b>Укажи текст, который надо спрятать</b>",
        "longread": (
            "🗄 <b>Это - лонгрид</b>\n<i>Нажми на кнопку, чтобы показать текст!\nОна"
            " активна в течение 6 часов</i>"
        ),
        "_cmd_doc_lr": "<text> - Создать лонгрид",
        "_cls_doc": "Пакует лонгриды под спойлеры",
    }

    async def lrcmd(self, message: Message):
        """<text> - Create new hidden message"""
        args = utils.get_args_raw(message)
        if not args:
            return

        await self.inline.form(
            self.strings("longread"),
            message,
            reply_markup={
                "text": "📖 Open spoiler",
                "callback": self._handler,
                "args": (args,),
            },
            disable_security=True,
        )

    async def lr_inline_handler(self, query: InlineQuery):
        """Create new hidden message"""
        text = query.args

        if not text:
            return await query.e400()

        return {
            "title": "Create new longread",
            "description": "ℹ This will create button-spoiler",
            "thumb": "https://img.icons8.com/external-wanicon-flat-wanicon/64/000000/external-read-free-time-wanicon-flat-wanicon.png",
            "message": self.strings("longread"),
            "reply_markup": {
                "text": "📖 Open spoiler",
                "callback": self._handler,
                "args": (text,),
                "disable_security": True,
            },
        }

    async def _handler(self, call: InlineCall, text: str):
        """Process button presses"""
        await call.edit(text)
        await call.answer()
