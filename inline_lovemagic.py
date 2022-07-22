#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# scope: hikka_min 1.2.10

# meta pic: https://img.icons8.com/color/480/000000/filled-like.png
# meta banner: https://mods.hikariatama.ru/badges/inline_lovemagic.jpg
# meta developer: @hikarimods
# scope: inline
# scope: hikka_only

import asyncio
import random
from asyncio import sleep

from telethon.tl.types import Message

from .. import loader, utils
from ..inline.types import InlineCall


@loader.tds
class ILYMod(loader.Module):
    """Famous TikTok hearts animation implemented in Hikka w/o logspam"""

    strings = {
        "name": "LoveMagicInline",
        "message": "<b>❤️‍🔥 I want to tell you something...</b>\n<i>{}</i>",
    }

    strings_ru = {
        "message": "<b>❤️‍🔥 Я хочу тебе сказать кое-что...</b>\n<i>{}</i>",
        "_cmd_doc_ily": "Отправляет сообщение с анимированными сердечками",
        "_cmd_doc_ilymate": "Отправляет сообщение с анимированными сердчеками v2",
        "_cls_doc": "Известная TikTok анимация сердечек без спама в логи и флудвейтов",
    }

    async def inline__handler(self, call: InlineCall, text: str):
        arr = ["❤️", "🧡", "💛", "💚", "💙", "💜", "🤎", "🖤", "💖"]
        h = "🤍"
        frames = [
            "".join(
                [
                    h * 9,
                    "\n",
                    h * 2,
                    i * 2,
                    h,
                    i * 2,
                    h * 2,
                    "\n",
                    h,
                    i * 7,
                    h,
                    "\n",
                    h,
                    i * 7,
                    h,
                    "\n",
                    h,
                    i * 7,
                    h,
                    "\n",
                    h * 2,
                    i * 5,
                    h * 2,
                    "\n",
                    h * 3,
                    i * 3,
                    h * 3,
                    "\n",
                    h * 4,
                    i,
                    h * 4,
                    "\n",
                    h * 9,
                ]
            )
            for i in arr
        ] + [
            "".join(
                [
                    h * 9,
                    "\n",
                    h * 2,
                    random.choice(arr),
                    random.choice(arr),
                    h,
                    random.choice(arr),
                    random.choice(arr),
                    h * 2,
                    "\n",
                    h,
                    random.choice(arr),
                    random.choice(arr),
                    random.choice(arr),
                    random.choice(arr),
                    random.choice(arr),
                    random.choice(arr),
                    random.choice(arr),
                    h,
                    "\n",
                    h,
                    random.choice(arr),
                    random.choice(arr),
                    random.choice(arr),
                    random.choice(arr),
                    random.choice(arr),
                    random.choice(arr),
                    random.choice(arr),
                    h,
                    "\n",
                    h,
                    random.choice(arr),
                    random.choice(arr),
                    random.choice(arr),
                    random.choice(arr),
                    random.choice(arr),
                    random.choice(arr),
                    random.choice(arr),
                    h,
                    "\n",
                    h * 2,
                    random.choice(arr),
                    random.choice(arr),
                    random.choice(arr),
                    random.choice(arr),
                    random.choice(arr),
                    h * 2,
                    "\n",
                    h * 3,
                    random.choice(arr),
                    random.choice(arr),
                    random.choice(arr),
                    h * 3,
                    "\n",
                    h * 4,
                    random.choice(arr),
                    h * 4,
                    "\n",
                    h * 9,
                ]
            )
            for _ in range(6)
        ]
        fourth = "".join(
            [
                h * 9,
                "\n",
                h * 2,
                arr[0] * 2,
                h,
                arr[0] * 2,
                h * 2,
                "\n",
                h,
                arr[0] * 7,
                h,
                "\n",
                h,
                arr[0] * 7,
                h,
                "\n",
                h,
                arr[0] * 7,
                h,
                "\n",
                h * 2,
                arr[0] * 5,
                h * 2,
                "\n",
                h * 3,
                arr[0] * 3,
                h * 3,
                "\n",
                h * 4,
                arr[0],
                h * 4,
                "\n",
                h * 9,
            ]
        )
        await call.edit(fourth)
        for _ in range(10):
            fourth = fourth.replace("🤍", "❤️‍🔥", 4)
            frames += [fourth]

        frames += [(arr[0] * (8 - i) + "\n") * (8 - i) for i in range(8)] + [
            f'<b>{" ".join(text.split()[: i + 1])}</b>'
            for i in range(len(text.split()))
        ]

        await self.animate(call, frames, interval=0.5, inline=True)

        await sleep(10)
        await call.edit(
            f"<b>{text}</b>",
            reply_markup={"text": "💔 Хочу также!", "url": "https://t.me/hikka_talks"},
        )

        await call.unload()

    async def inline__handler_gay(self, call: InlineCall, text: str):
        heart_template = """
            🤍🤍🧡🧡🤍🤍🤍🧡🧡🤍🤍
            🤍🧡🧡🧡🧡🤍🧡🧡🧡🧡🤍
            🧡🧡🧡🧡🧡🧡🧡🧡🧡🧡🧡
            🧡🧡🧡🧡🧡🧡🧡🧡🧡🧡🧡
            🧡🧡🧡🧡🧡🧡🧡🧡🧡🧡🧡
            🤍🧡🧡🧡🧡🧡🧡🧡🧡🧡🤍
            🤍🤍🧡🧡🧡🧡🧡🧡🧡🤍🤍
            🤍🤍🤍🧡🧡🧡🧡🧡🤍🤍🤍
            🤍🤍🤍🤍🧡🧡🧡🤍🤍🤍🤍
            🤍🤍🤍🤍🤍🧡🤍🤍🤍🤍🤍""".splitlines()

        hearts = ["❤️", "🧡", "💛", "💚", "💙", "💜"]
        await self.animate(
            call,
            [
                "\n".join(
                    [
                        "<code>"
                        + line.strip().replace(
                            "🧡", hearts[(i + offset) % (len(hearts) - 1)], 13
                        )
                        + "</code>"
                        for i, line in enumerate(heart_template[1:])
                    ]
                )
                for offset in range(16)
            ]
            + [
                f'<b>{" ".join(text.split()[: i + 1])}</b>'
                for i in range(len(text.split()))
            ],
            interval=0.5,
            inline=True,
        )

        await sleep(10)
        await call.edit(
            f"<b>{text}</b>",
            reply_markup={"text": "💔 Хочу также!", "url": "https://t.me/hikka_talks"},
        )

    async def ilycmd(self, message: Message):
        """Send inline message with animated hearts"""
        args = utils.get_args_raw(message)
        await self.inline.form(
            self.strings("message").format("*" * (len(args) or 9)),
            reply_markup={
                "text": "🧸 Open",
                "callback": self.inline__handler,
                "args": (args or "I ❤️ you!",),
            },
            message=message,
            disable_security=True,
        )

    async def ilymatecmd(self, message: Message):
        """Send inline message with animated hearts v2"""
        args = utils.get_args_raw(message)
        await self.inline.form(
            self.strings("message").format("*" * (len(args) or 21)),
            reply_markup={
                "text": "🧸 Open",
                "callback": self.inline__handler_gay,
                "args": (args or "I am gay and I 💙 you!",),
            },
            message=message,
            disable_security=True,
        )
