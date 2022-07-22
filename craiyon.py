# █ █ ▀ █▄▀ ▄▀█ █▀█ ▀    ▄▀█ ▀█▀ ▄▀█ █▀▄▀█ ▄▀█
# █▀█ █ █ █ █▀█ █▀▄ █ ▄  █▀█  █  █▀█ █ ▀ █ █▀█
#
#              © Copyright 2022
#
#          https://t.me/hikariatama
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://img.icons8.com/external-kmg-design-flat-kmg-design/344/external-draw-graphic-design-kmg-design-flat-kmg-design.png
# meta banner: https://mods.hikariatama.ru/badges/craiyon.jpg
# meta developer: @hikariatama
# scope: hikka_min 1.2.10

import base64
from .. import loader, utils
from telethon.tl.types import Message
import requests


@loader.tds
class CrAIyonMod(loader.Module):
    """Generates images by description using Craiyon AI (DALL-E)"""

    strings = {
        "name": "CrAIyon",
        "args": "🚫 <b>No photo description specified</b>",
        "generating": (
            "🖌 <b>Drawing request </b><code>{}</code><b> using craiyon. Be patient,"
            " this takes some time</b>"
        ),
        "error": "🚫 <b>I can't draw </b><code>{}</code>",
        "drawing": "🖌 <b>This is delicious </b><code>{}</code>",
    }

    async def craiyoncmd(self, message: Message):
        """<description> - Generate an image by description using Craiyon AI (DALL-E)"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings("args"))
            return

        form = await self.inline.form(
            self.strings("generating").format(utils.escape_html(args)),
            message=message,
            gif="https://pa1.narvii.com/6074/b2f0163e5dd1ff7ee6582e1e032eb906b25228ac_hq.gif",
            silent=True,
            reply_markup={"text": "🧑‍🎨 Im the drower", "data": "empty"},
            ttl=24 * 60 * 60,
        )

        result = (
            await utils.run_sync(
                requests.post,
                "https://backend.craiyon.com/generate",
                json={"prompt": args},
                headers={
                    "accept": "application/json",
                    "accept-encoding": "gzip, deflate, br",
                    "accept-language": "en-US,en;q=0.9,ru;q=0.8",
                    "content-type": "application/json",
                    "origin": "https://www.craiyon.com",
                    "referer": "https://www.craiyon.com/",
                    "user-agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                        " (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"
                    ),
                },
            )
        ).json()

        if not result.get("images"):
            await form.edit(
                self.strings("error").format(args),
                reply_markup=None,
                gif="https://data.whicdn.com/images/61134119/original.gif",
            )
            return

        images = [base64.b64decode(i.encode()) for i in result["images"]]
        await message.respond(self.strings("drawing").format(args), file=images)
        await form.delete()
