#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# scope: hikka_min 1.2.10

# meta pic: https://img.icons8.com/color/480/000000/angry--v1.png
# meta banner: https://mods.hikariatama.ru/badges/insult.jpg
# meta developer: @hikarimods

import random

from telethon.tl.types import Message

from .. import loader, utils


@loader.tds
class PoliteInsultMod(loader.Module):
    """If you need to insult but to be intelligent"""

    strings = {
        "name": "PoliteInsult",
        "insult": (
            "<emoji document_id=5373123633415723713>🤬</emoji> {} you are {} {}"
            " {} {}"
        ),
        "adjectives_start": [
            "temperamental",
            "rude",
            "silly to me",
            "arrogant",
            "non-individualistic",
            "undisciplined",
            "unprofessional",
            "irresponsible",
            "reckless",
            "indifferent to me",
        ],
        "nouns": ["participant of this group chat", "this world citizen"],
        "starts": [
            (
                "I don't want to jump to conclusions and I certainly can't claim, and"
                " this is my subjective opinion, but"
            ),
            (
                "Having analyzed the situation, I can express my subjective opinion. It"
                " lies in the fact that"
            ),
            (
                "Not trying to make anyone feel bad, but just expressing my humble"
                " point of view, which does not affect other people's points of view, I"
                " can say that"
            ),
            (
                "Without intending to affect any social minorities, I would like to say"
                " that"
            ),
        ],
    }

    strings_ru = {
        "insult": (
            "<emoji document_id=5373123633415723713>🤬</emoji> {} ты - {} {} {} {}"
        ),
        "adjectives_start": [
            "вспыльчивый(-ая)",
            "невоспитанный(-ая)",
            "осточертевший(-ая) мне",
            "глуповатый(-ая)",
            "надменный(-ая)",
            "неиндивидуалистичный(-ая)",
            "индифферентный(-ая)",
            "недисциплинированный(-ая)",
            "непрофессиональный(-ая)",
            "безответственный(-ая)",
            "безрассудный(-ая)",
            "безразличный(-ая) мне",
        ],
        "nouns": ["участник(-ца) данного чата", "житель(-ница) мира сего"],
        "starts": [
            "Не хочу делать поспешных выводов, но",
            "Я, конечно, не могу утверждать, и это мое субъективное мнение, но",
            (
                "Проанализировав ситуацию, я могу высказать свое субъективное мнение."
                " Оно заключается в том, что"
            ),
            (
                "Не пытаясь никого оскорбить, а лишь высказывая свою скромную точку"
                " зрения, которая не влияет на точку зрения других людей, могу"
                " сказать, что"
            ),
            (
                "Не преследуя попытку затронуть какие-либо социальные меньшинства, хочу"
                " сказать, что"
            ),
        ],
    }

    async def insultocmd(self, message: Message):
        """Use when angry"""
        await utils.answer(
            message,
            self.strings("insult").format(
                random.choice(self.strings("starts")),
                random.choice(self.strings("adjectives_start")),
                random.choice(self.strings("adjectives_start")),
                random.choice(self.strings("nouns")),
                random.choice(["!!!!", "!", "."]),
            ),
        )
