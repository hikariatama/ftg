#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# scope: hikka_min 1.2.10

# meta pic: https://img.icons8.com/fluency/452/texshop.png
# meta developer: @hikarimods

import io
import logging

import matplotlib.pyplot as plt
from telethon.tl.types import Message

from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class LaTeXMod(loader.Module):
    """Renders mathematical formulas in LaTeX pngs"""

    strings = {
        "name": "LaTeX",
        "no_args": "🚫 <b>Specify a formula to render</b>",
        "cant_render": "🚫 <b>Can't render formula</b>",
    }

    strings_ru = {
        "no_args": "🚫 <b>Укажи формулу для рендера</b>",
        "cant_render": "🚫 <b>В формуле обнаружена ошибка</b>",
    }

    async def latexcmd(self, message: Message):
        """<formula> - Create LaTeX render"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings("no_args"))
            return

        try:
            tex = f"${args}$"

            fig = plt.figure()
            ax = fig.add_axes([0, 0, 1, 1])
            ax.set_axis_off()

            t = ax.text(
                0.5,
                0.5,
                tex,
                horizontalalignment="center",
                verticalalignment="center",
                fontsize=25,
                color="black",
            )

            ax.figure.canvas.draw()

            bbox = t.get_window_extent()
            fig.set_size_inches(bbox.width / 80, bbox.height / 80)
            buf = io.BytesIO()
            plt.savefig(buf)
            buf.seek(0)
        except Exception:
            logger.exception("Can't render formula")
            await utils.answer(message, self.strings("cant_render"))
            return

        await self._client.send_file(
            message.peer_id,
            buf.getvalue(),
            reply_to=message.reply_to_msg_id,
            caption=f"🧮 <b>LaTeX</b>: <code>{args}</code>",
        )

        if message.out:
            await message.delete()
