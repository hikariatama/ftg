"""
    Copyright 2021 t.me/hikariatama
    Licensed under the Apache License, Version 2.0
    
    Author is not responsible for any consequencies caused by using this
    software or any of its parts. If you have any questions or wishes, feel
    free to contact Dan by sending pm to @hikari_alt.
"""

#<3 title: PoliteInsult
#<3 pic: https://img.icons8.com/fluency/48/000000/angry.png
#<3 desc: Когда хочешь накричать на человека, но оставаться интеллигентом

from .. import loader, utils

import logging
import random


logger = logging.getLogger(__name__)


@loader.tds
class PoliteInsultMod(loader.Module):
    """Очень вежливая версия известного модуля"""
    strings = {"name": "PoliteInsult"}

    async def insultocmd(self, message):
        """Используйте, когда злитесь"""
        adjectives_start = ["вспыльчивый(-ая)", "невоспитанный(-ая)", "осточертевший(-ая) мне", "глуповатый(-ая)",
                            "надменный(-ая)", "неиндивидуалистичный(-ая)", "неиндифферентный(-ая)", "недисциплинированный(-ая)"]
        nouns = ["человек", "участник(-ца) данного чата"]
        starts = ["Не хочу делать поспешных выводов, но", "Я, конечно, не могу утверждать, и это мое субъективное мнение, но", "Проанализировав ситуацию, я могу высказать свое субъективное мнение. Оно заключается в том, что",
                  "Не пытаясь никого осокорбить, а лишь высказывая свою скромную точку зрения, которая не влияет на точку зрения других людей, могу сказать, что", "Не преследуя попытку затронуть какие-либо социальные меньшинства, хочу сказать, что"]
        ends = ["!!!!", "!", "."]
        start = random.choice(starts)
        adjective_start = random.choice(adjectives_start)
        adjective_mid = random.choice(adjectives_start)
        noun = random.choice(nouns)
        end = random.choice(ends)
        insult = start + " ты - " + adjective_start + " " + \
            adjective_mid + (" " if adjective_mid else "") + noun + end
        logger.debug(insult)
        await utils.answer(message, insult)
