__version__ = (2, 0, 0)

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

import asyncio
import base64
import hashlib
import typing
import warnings

import requests

from .. import loader, utils

warnings.filterwarnings("ignore")

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

    strings = {"name": "CheckEge"}

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "CHECKEGE_TOKEN",
                None,
                (
                    "Токен CheckEge. Можно получить на https://checkege.rustest.ru из"
                    " куки Participant. Если заполнить остальные поля конфига, при"
                    " авторизации заполнится автоматически."
                ),
                validator=loader.validators.Hidden(),
            ),
            loader.ConfigValue(
                "FIO",
                None,
                (
                    "ФИО, с которым нужно авторизоваться в формате Иванов Иван"
                    " Иванович. Требует наличия RuCaptcha токена в конфиге."
                ),
                validator=loader.validators.Hidden(),
            ),
            loader.ConfigValue(
                "DOCUMENT",
                None,
                "Номер паспорта без серии. Требует наличия RuCaptcha токена в конфиге.",
                validator=loader.validators.Hidden(
                    loader.validators.RegExp(r"^\d{6}$")
                ),
            ),
            loader.ConfigValue(
                "REGION",
                None,
                (
                    "Код региона, в котором вы сдавали ЕГЭ. Можно посмотреть в"
                    " https://gist.github.com/hikariatama/95f1a92dbe0379a88b6e673a1d79ed17."
                    " Требует наличия RuCaptcha токена в конфиге."
                ),
                validator=loader.validators.Hidden(
                    loader.validators.RegExp(r"^\d{1,2}$")
                ),
            ),
            loader.ConfigValue(
                "RUCAPTCHA_TOKEN",
                None,
                "Токен RuCaptcha. Можно получить на https://rucaptcha.com",
                validator=loader.validators.Hidden(),
            ),
            loader.ConfigValue(
                "PROXY",
                None,
                "Прокси в формате http://user:pass@host:port",
                validator=loader.validators.Hidden(),
            ),
        )

    async def _auth(self):
        captcha = (
            await utils.run_sync(
                requests.get,
                "https://checkege.rustest.ru/api/captcha",
                proxies={"https": self.config["PROXY"]},
                verify=False,
            )
        ).json()

        captcha_img = base64.b64decode(captcha["Image"].encode())
        captcha_token = captcha["Token"]

        captcha_id = (
            await utils.run_sync(
                requests.post,
                "https://rucaptcha.com/in.php",
                data={
                    "key": self.config["RUCAPTCHA_TOKEN"],
                    "method": "post",
                    "numeric": 1,
                    "min_len": 6,
                    "max_len": 6,
                },
                files={
                    "file": ("captcha.png", captcha_img, "image/png"),
                },
                proxies={"https": self.config["PROXY"]},
            )
        ).text.split("|")[1]

        while True:
            await asyncio.sleep(3)
            captcha_result = (
                await utils.run_sync(
                    requests.get,
                    "https://rucaptcha.com/res.php",
                    params={
                        "key": self.config["RUCAPTCHA_TOKEN"],
                        "action": "get",
                        "id": captcha_id,
                    },
                    proxies={"https": self.config["PROXY"]},
                )
            ).text

            if captcha_result != "CAPCHA_NOT_READY":
                break

        captcha_result = captcha_result.split("|")[1]

        self.config["CHECKEGE_TOKEN"] = dict(
            (
                await utils.run_sync(
                    requests.post,
                    "https://checkege.rustest.ru/api/participant/login",
                    data={
                        "Hash": hashlib.md5(
                            self.config["FIO"].replace(" ", "").lower().encode()
                        ).hexdigest(),
                        "Code": "",
                        "Document": f"000000{self.config['DOCUMENT']}",
                        "Region": self.config["REGION"],
                        "AgreeCheck": "on",
                        "Captcha": captcha_result,
                        "Token": captcha_token,
                        "reCaptureToken": captcha_result,
                    },
                    verify=False,
                    proxies={"https": self.config["PROXY"]},
                )
            ).cookies
        )["Participant"]

    async def _get_result(self, retry: bool = True) -> typing.Union[dict, bool]:
        if not self.config["CHECKEGE_TOKEN"] and (
            not self.config["FIO"]
            or not self.config["DOCUMENT"]
            or not self.config["REGION"]
        ):
            return False

        if not self.config["CHECKEGE_TOKEN"]:
            await self._auth()

        result = (
            await utils.run_sync(
                requests.get,
                "https://checkege.rustest.ru/api/exam",
                cookies={"Participant": self.config["CHECKEGE_TOKEN"]},
                verify=False,
                proxies={"https": self.config["PROXY"]},
            )
        ).json()

        if result.get("Message") == "Authorization has been denied for this request.":
            if retry:
                await self._auth()
                return await self._get_result(retry=False)

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
                    else (
                        "<emoji document_id=5462882007451185227>🚫</emoji>"
                        " <b>незачёт</b>"
                    )
                )
                if name == "Сочинение"
                else (
                    "<emoji document_id=5465465194056525619>👍</emoji>"
                    f" <b>{test_mark} балл(-ов)</b>"
                    if has_result
                    else (
                        "<emoji document_id=5462882007451185227>🚫</emoji> <b>нет"
                        " результата</b>"
                    )
                )
            )
            strings += f"{emoji} <b>{name}</b> · {result}\n"

        return strings

    def _update_current_results(self, result: dict):
        self.set(
            "have_results",
            [
                (exam["ExamId"], exam["TestMark"])
                for exam in result["Result"]["Exams"]
                if exam["HasResult"]
            ],
        )

    @loader.command()
    async def checkege(self, message):
        """Авторизоваться и вывести результаты ЕГЭ"""
        if not self.config["CHECKEGE_TOKEN"] and (
            not self.config["FIO"]
            or not self.config["DOCUMENT"]
            or not self.config["REGION"]
        ):
            await utils.answer(
                message,
                (
                    "<emoji document_id=5462882007451185227>🚫</emoji> <b>Токен"
                    " CheckEge не установлен.</b>\n\nАвторизуйтесь на"
                    " https://checkege.rustest.ru и получите его из cookie Participant"
                ),
            )
            return

        message = await utils.answer(
            message,
            (
                "<emoji document_id=5465443379917629504>🔓</emoji> <b>Взламываю"
                " ФИПИ...</b>"
            ),
        )
        if not (result := await self._get_result()):
            await utils.answer(
                message,
                (
                    "<emoji document_id=5463186335948878489>⚰️</emoji> <b>Неверный токен"
                    " / данные авторизации!</b>"
                ),
            )
            self.set("authorized", False)
            return

        await utils.answer(message, await self._format_result(result))
        self.set("authorized", True)

    @loader.loop(interval=30, autostart=True)
    async def check_loop(self):
        if not self.get("authorized"):
            return

        if not (result := await self._get_result()):
            await self.inline.bot.send_message(
                self._tg_id,
                (
                    "⚰️ <b>Авторизация на CheckEge истекла, авторизоваться не"
                    " получилось!</b>"
                ),
            )

            self.set("authorized", False)
            return

        for exam in result["Result"]["Exams"]:
            if exam["HasResult"] and (exam["ExamId"], exam["TestMark"]) not in self.get(
                "have_results", []
            ):
                await self.inline.bot.send_message(
                    self._tg_id,
                    (
                        f"🎉 Получен результат за экзамен <b>{exam['Subject']}</b>:"
                        f" <b>{exam['TestMark']} балл(-ов)</b>"
                    ),
                )

        self._update_current_results(result)
