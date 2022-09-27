#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://img.icons8.com/stickers/344/love-message.png
# meta developer: @hikarimods
# meta banner: https://mods.hikariatama.ru/badges/declaration.jpg
# scope: hikka_only

import asyncio
import random
import time
from telethon.tl.types import Message
import logging

from .. import loader, utils
from ..inline.types import BotMessage

logger = logging.getLogger(__name__)


@loader.tds
class Declaration(loader.Module):
    """If you are too humble to declare your love, sympathy or hate, use this module"""

    strings = {
        "name": "Declaration",
        "not_private": (
            "<emoji document_id=6053166094816905153>💀</emoji> <b>This command must be"
            " run in personal messages...</b>"
        ),
        "ily": (
            "<emoji document_id=5465143921912846619>💭</emoji> <b>You have 1 new"
            ' message. <a href="https://t.me/{}?start=read_{}">Please, read it</a></b>'
        ),
        "ily_love": [
            "👋 <i>Hi. I'm <b>Hikka</b>.</i>",
            (
                "🫣 <i>My owner is very humble to say something, so he asked me to help"
                " him...</i>"
            ),
            "🥰 <i>He just wanted you to know, that <b>he loves you</b>...</i>",
            "🤗 <i>These are sincere feelings... Please, don't blame him.</i>",
            "🫶 <i>Better say him some warm words... 🙂</i>",
        ],
        "ily_symp": [
            "👋 <i>Hi. I'm <b>Hikka</b>.</i>",
            (
                "🫣 <i>My owner is very humble to say something, so he asked me to help"
                " him...</i>"
            ),
            "🥰 <i>He just wanted you to know, that <b>he likes you</b>...</i>",
            "🤗 <i>These are sincere feelings... Please, don't blame him.</i>",
            "🫶 <i>Better go hug him!... 🙂</i>",
        ],
        "ily_hate": [
            "👋 <i>Hi. I'm <b>Hikka</b>.</i>",
            (
                "🗿 <i>My owner doesn't want to waste time on you, so he asked me to do"
                " this instead...</i>"
            ),
            "🤬 <i>He just wanted you to know, that <b>he hates you</b>...</i>",
            "🖕 <i>These are sincere feelings... Please, go fuck yourself.</i>",
            (
                "👿 <i>Never ever write to person below again. Eat shit and die,"
                " sucker.</i>"
            ),
        ],
        "talk": "🫰 Talk",
        "404": "😢 <b>Message has already disappeared. You can't read it now...</b>",
        "read": "🫰 <b>{} has read your declaration ({})</b>",
        "args": (
            "<emoji document_id=6053166094816905153>💀</emoji> <b>Wrong arguments...</b>"
        ),
    }

    strings_ru = {
        "not_private": (
            "<emoji document_id=6053166094816905153>💀</emoji> <b>Эту команду нужно"
            " выполнять в личных сообщениях...</b>"
        ),
        "ily": (
            "<emoji document_id=5465143921912846619>💭</emoji> <b>У вас 1 новое"
            ' сообщение. <a href="https://t.me/{}?start=read_{}">Пожалуйста, прочтите'
            " его</a></b>"
        ),
        "ily_love": [
            "👋 <i>Привет. Я <b>Хикка</b>.</i>",
            (
                "🫣 <i>Мой хозяин очень стеснительно не хочет сказать что-то, поэтому он"
                " попросил меня помочь ему...</i>"
            ),
            "🥰 <i>Он просто хотел, чтобы Вы знали, что <b>он любит Вас</b>...</i>",
            "🤗 <i>Это искренние чувства... Пожалуйста, не злитесь на него.</i>",
            "🫶 <i>Лучше скажите ему несколько теплых слов... 🙂</i>",
        ],
        "ily_symp": [
            "👋 <i>Привет. Я <b>Хикка</b>.</i>",
            (
                "🫣 <i>Мой хозяин очень стеснительно не хочет сказать что-то, поэтому он"
                " попросил меня помочь ему...</i>"
            ),
            "🥰 <i>Он просто хотел, чтобы Вы знали, что <b>Вы ему нравитесь</b>...</i>",
            "🤗 <i>Это искренние чувства... Пожалуйста, не злитесь на него.</i>",
            "🫶 <i>Лучше пойдите и обнимите его!... 🙂</i>",
        ],
        "ily_hate": [
            "👋 <i>Привет. Я <b>Хикка</b>.</i>",
            (
                "🗿 <i>Мой хозяин не хочет тратить время на вас, поэтому он попросил"
                " меня сделать это вместо него...</i>"
            ),
            "🤬 <i>Он просто хотел, чтобы вы знали, что <b>он ненавидит вас</b>...</i>",
            "🖕 <i>Это искренние чувства... Пожалуйста, идите нахуй.</i>",
            (
                "👿 <i>Никогда больше не пишите нижеуказанному человеку. Пожрите дерьма"
                " и сдохните, уебок.</i>"
            ),
        ],
        "talk": "🫰 Поговорить",
        "404": "😢 <b>Сообщение уже исчезло. Вы не можете его прочитать...</b>",
        "read": "🫰 <b>{} прочитал ваше признание ({})</b>",
        "args": (
            "<emoji document_id=6053166094816905153>💀</emoji> <b>Неверные"
            " аргументы...</b>"
        ),
    }

    async def client_ready(self):
        self.ids = self.pointer("ids", {})

    @loader.command(ru_doc="[hate/symp/love] - Признаться в чем-то")
    async def declare(self, message: Message):
        """[hate/symp/love] - Declare something"""
        if not message.is_private:
            await utils.answer(message, self.strings("not_private"))
            return

        args = utils.get_args_raw(message)
        if args and args not in {"hate", "symp", "love"}:
            await utils.answer(message, self.strings("args"))
            return

        if not args:
            args = "love"

        id_ = utils.rand(8)
        await utils.answer(
            message, self.strings("ily").format(self.inline.bot_username, id_)
        )
        self.ids[id_] = {"type": args, "exp": int(time.time()) + 24 * 60 * 60}

    async def aiogram_watcher(self, message: BotMessage):
        if not message.text.startswith("/start read_"):
            return

        for id_, info in self.ids.copy().items():
            if info["exp"] < int(time.time()):
                self.ids.pop(id_)
                continue

        id_ = message.text.split("_")[1]
        if id_ not in self.ids:
            await message.answer(self.strings("404"))
            return

        info = self.ids.pop(id_)
        for m in self.strings(f"ily_{info['type']}")[:-1]:
            await message.answer(m)
            await asyncio.sleep(random.randint(350, 400) / 100)

        await self.inline.bot.send_message(
            self._client.tg_id,
            self.strings("read").format(
                utils.escape_html(message.from_user.full_name),
                info["type"],
            ),
        )

        await message.answer(
            self.strings(f"ily_{info['type']}")[-1],
            reply_markup=self.inline.generate_markup(
                {
                    "text": self.strings("talk"),
                    "url": f"tg://user?id={self._client.tg_id}",
                }
            ),
        )
