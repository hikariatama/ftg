# ©️ Dan Gazizullin, 2021-2023
# This file is a part of Hikka Userbot
# Code is licensed under CC-BY-NC-ND 4.0 unless otherwise specified.
# 🌐 https://github.com/hikariatama/Hikka
# 🔑 https://creativecommons.org/licenses/by-nc-nd/4.0/
# + attribution
# + non-commercial
# + no-derivatives

# You CANNOT edit this file without direct permission from the author.
# You can redistribute this file without any changes.

# meta pic: https://0x0.st/Hcj1.png
# meta banner: https://mods.hikariatama.ru/badges/checkege.jpg

# meta developer: @hikarimods
# scope: hikka_only
# scope: hikka_min 1.6.2

import typing
import warnings

import requests

from .. import loader, utils

SUBJECT_MAPPING = {
    "Русский": "<emoji document_id=5449408995691341691>🇷🇺</emoji>",
    "Математика": "<emoji document_id=5226470789682833538>➗</emoji>",
    "Физика": "<emoji document_id=5373039692574893940>👨‍🏫</emoji>",
    "География": "<emoji document_id=5454093069844487380>🗺</emoji>",
    "Информатика": "<emoji document_id=5431376038628171216>💻</emoji>",
    "Английский": "<emoji document_id=5202196682497859879>🇬🇧</emoji>",
    "Немецкий": "<emoji document_id=5409360418520967565>🇩🇪</emoji>",
    "Французский": "<emoji document_id=5202132623060640759>🇫🇷</emoji>",
    "Китайский": "<emoji document_id=5431782733376399004>🇨🇳</emoji>",
    "Общество": "<emoji document_id=5372926953978341366>👥</emoji>",
    "История": "<emoji document_id=5190941656274181429>👵</emoji>",
    "Литература": "<emoji document_id=5373098009640836781>📚</emoji>",
    "Химия": "<emoji document_id=5411512278740640309>🧪</emoji>",
    "Биология": "<emoji document_id=5460905716904633427>😺</emoji>",
}


@loader.tds
class CheckEge(loader.Module):
    """Checks Russian National Exam results"""

    strings = {
        "name": "CheckEge",
        "no_token": (
            "<emoji document_id=5462882007451185227>🚫</emoji> <b>Токен CheckEge не"
            " установлен.</b>\n\nАвторизуйтесь на https://checkege.rustest.ru и"
            " получите его из cookie Participant"
        ),
        "checking": (
            "<emoji document_id=5465443379917629504>🔓</emoji> <b>Взламываю ФИПИ...</b>"
        ),
        "wrong_token": (
            "<emoji document_id=5463186335948878489>⚰️</emoji> <b>Неверный токен!</b>"
        ),
        "auth_expired": (
            "⚰️ <b>Авторизация на CheckEge истекла. Пожалуйста, повторите команду</b>"
            " <code>{}checkege</code> <b>для продолжения.</b>"
        ),
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "CHECKEGE_TOKEN",
                None,
                (
                    "CheckEge token. Login to https://checkege.rustest.ru and get it"
                    " from the cookie Participant"
                ),
                validator=loader.validators.Hidden(),
            )
        )

    def _fetch_result_sync(self) -> dict:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = requests.get(
                "https://checkege.rustest.ru/api/exam",
                cookies={"Participant": self.config["CHECKEGE_TOKEN"]},
                verify=False,
            ).json()

        return result

    async def _get_result(self) -> typing.Union[dict, bool]:
        result = await utils.run_sync(self._fetch_result_sync)
        if result.get("Message") == "Authorization has been denied for this request.":
            return False

        return result

    async def _format_result(self, result: dict) -> str:
        strings = ""
        for exam in result["Result"]["Exams"]:
            name, has_result, test_mark = (
                exam["Subject"],
                exam["HasResult"],
                exam["TestMark"],
            )
            emoji = next(
                (SUBJECT_MAPPING.get(n) for n in SUBJECT_MAPPING if n in name),
                "<emoji document_id=5470089812977391436>📕</emoji>",
            )

            result = (
                (
                    "<emoji document_id=5465465194056525619>👍</emoji> <b>зачёт</b>"
                    if has_result and test_mark
                    else "<emoji document_id=5462882007451185227>🚫</emoji> <b>незачёт</b>"
                )
                if name == "Сочинение"
                else (
                    "<emoji document_id=5465465194056525619>👍</emoji>"
                    f" <b>{test_mark} балл(-ов)</b>"
                    if has_result
                    else (
                        "<emoji document_id=5462882007451185227>🚫</emoji> <b>нет результата</b>"
                    )
                )
            )
            strings += f"{emoji} <b>{name}</b> ·" f" {result}\n"

        return strings

    def _update_current_results(self, result: dict):
        self.set(
            "have_results",
            [exam["ExamId"] for exam in result["Result"]["Exams"] if exam["HasResult"]],
        )

    @loader.command()
    async def checkege(self, message):
        """Проверить авторизацию и вывести результаты ЕГЭ"""
        if not self.config["CHECKEGE_TOKEN"]:
            await utils.answer(message, self.strings("no_token"))
            return

        message = await utils.answer(message, self.strings("checking"))
        if not (result := await self._get_result()):
            await utils.answer(message, self.strings("wrong_token"))
            self.set("authorized", False)
            return

        await utils.answer(message, await self._format_result(result))
        self.set("authorized", True)

    @loader.loop(interval=5 * 60, autostart=True)
    async def check_loop(self):
        if not self.get("authorized"):
            return

        if not (result := await self._get_result()):
            await self.inline.bot.send_message(
                self._tg_id,
                self.strings("auth_expired").format(
                    utils.escape_html(self.get_prefix())
                ),
            )

            self.set("authorized", False)
            return

        for exam in result["Result"]["Exams"]:
            if exam["HasResult"] and exam["ExamId"] not in self.get("have_results", []):
                await self.inline.bot.send_message(
                    self._tg_id,
                    (
                        f"🎉 Получен результат за экзамен <b>{exam['Subject']}</b>:"
                        f" <b>{exam['TestMark']} балл(-ов)</b>"
                    ),
                )
                self._update_current_results(result)
