__version__ = (1, 0, 1)
# █ █ ▀ █▄▀ ▄▀█ █▀█ ▀    ▄▀█ ▀█▀ ▄▀█ █▀▄▀█ ▄▀█
# █▀█ █ █ █ █▀█ █▀▄ █ ▄  █▀█  █  █▀█ █ ▀ █ █▀█
#
#              © Copyright 2022
#
#          https://t.me/hikariatama
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://img.icons8.com/external-wanicon-flat-wanicon/64/000000/external-read-free-time-wanicon-flat-wanicon.png
# meta developer: @hikariatama
# scope: inline
# scope: hikka_only
# scope: hikka_min 1.1.6

from .. import loader
import logging
from ..inline.types import InlineQuery, InlineCall

logger = logging.getLogger(__name__)


@loader.tds
class LongReadMod(loader.Module):
    """Pack longreads under button spoilers"""

    strings = {
        "name": "LongRead",
        "no_text": "🚫 <b>Please, specify text to hide</b>",
        "longread": "🗄 <b>This is long read</b>\n<i>Click button to show text!\nThis button is active withing 6 hours</i>",
    }

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
