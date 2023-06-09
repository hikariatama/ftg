__version__ = (1, 0, 7)

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

# meta pic: https://img.icons8.com/fluency/512/artificial-intelligence.png
# meta banner: https://mods.hikariatama.ru/badges/anything.jpg
# meta developer: @hikarimods
# scope: hikka_only
# scope: hikka_min 1.6.2

import asyncio
import io
import json
import logging
import random
import re
import time

import requests
from hikkatl.types import Message

from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class Anything(loader.Module):
    """Draws ANYTHING using artificial intelligence. No API key required. 18+ only."""

    strings = {
        "name": "Anything",
        "args": (
            "<emoji document_id=5210952531676504517>❌</emoji> <b>Arguments are"
            " required</b>"
        ),
        "fail": (
            "<emoji document_id=5210952531676504517>❌</emoji> <b>Failed to generate"
            " image</b>"
        ),
        "drawing": (
            "<emoji document_id=5431456208487716895>🎨</emoji> <b>Drawing {}"
            " picture(-s)"
            " using </b><code>{}</code><b>...</b>"
        ),
        "ready": (
            "<emoji document_id=5398001711786762757>✅</emoji> <b>Image"
            " generated!</b>{}"
        ),
        "debug": (
            "\n\n<i>Model: {model}, CFG: {cfg}, Steps: {steps}, Prompt:"
            " {prompt}, Negative: {negative}, {took:.2f}s</i>"
        ),
    }

    strings_ru = {
        "args": (
            "<emoji document_id=5210952531676504517>❌</emoji> <b>Требуются"
            " аргументы</b>"
        ),
        "fail": (
            "<emoji document_id=5210952531676504517>❌</emoji> <b>Не удалось"
            " сгенерировать изображение</b>"
        ),
        "drawing": (
            "<emoji document_id=5431456208487716895>🎨</emoji> <b>Рисую {}"
            " картинку(-ок) с помощью </b><code>{}</code><b>...</b>"
        ),
        "ready": (
            "<emoji document_id=5398001711786762757>✅</emoji> <b>Изображение"
            " сгенерировано!</b>{}"
        ),
        "debug": (
            "\n\n<i>Модель: {model}, CFG: {cfg}, Шаги: {steps}, Запрос:"
            " {prompt}, Отрицательный запрос: {negative}, {took:.2f}s</i>"
        ),
    }

    strings_es = {
        "args": (
            "<emoji document_id=5210952531676504517>❌</emoji> <b>Se requieren"
            " argumentos</b>"
        ),
        "fail": (
            "<emoji document_id=5210952531676504517>❌</emoji> <b>No se"
            " pudo generar la imagen</b>"
        ),
        "drawing": (
            "<emoji document_id=5431456208487716895>🎨</emoji> <b>Dibujando {}"
            " imagen(-es) usando </b><code>{}</code><b>...</b>"
        ),
        "ready": (
            "<emoji document_id=5398001711786762757>✅</emoji> <b>¡Imagen"
            " generada!</b>{}"
        ),
        "debug": (
            "\n\n<i>Modelo: {model}, CFG: {cfg}, Pasos: {steps}, Solicitud:"
            " {prompt}, Solicitud negativa: {negative}, {took:.2f}s</i>"
        ),
    }

    strings_it = {
        "args": (
            "<emoji document_id=5210952531676504517>❌</emoji> <b>Sono richiesti"
            " argomenti</b>"
        ),
        "fail": (
            "<emoji document_id=5210952531676504517>❌</emoji> <b>Impossibile"
            " generare l'immagine</b>"
        ),
        "drawing": (
            "<emoji document_id=5431456208487716895>🎨</emoji> <b>Disegno {}"
            " immagine(-i) usando </b><code>{}</code><b>...</b>"
        ),
        "ready": (
            "<emoji document_id=5398001711786762757>✅</emoji> <b>Immagine"
            " generata!</b>{}"
        ),
        "debug": (
            "\n\n<i>Modello: {model}, CFG: {cfg}, Passi: {steps}, Richiesta:"
            " {prompt}, Richiesta negativa: {negative}, {took:.2f}s</i>"
        ),
    }

    strings_fr = {
        "args": (
            "<emoji document_id=5210952531676504517>❌</emoji> <b>Des arguments"
            " sont requis</b>"
        ),
        "fail": (
            "<emoji document_id=5210952531676504517>❌</emoji> <b>Impossible"
            " de générer l'image</b>"
        ),
        "drawing": (
            "<emoji document_id=5431456208487716895>🎨</emoji> <b>Dessin {}"
            " image(-s) en utilisant </b><code>{}</code><b>...</b>"
        ),
        "ready": (
            "<emoji document_id=5398001711786762757>✅</emoji> <b>Image générée!</b>{}"
        ),
        "debug": (
            "\n\n<i>Modèle: {model}, CFG: {cfg}, Étapes: {steps}, Demande:"
            " {prompt}, Demande négative: {negative}, {took:.2f}s</i>"
        ),
    }

    strings_de = {
        "args": (
            "<emoji document_id=5210952531676504517>❌</emoji> <b>Argumente"
            " werden benötigt</b>"
        ),
        "fail": (
            "<emoji document_id=5210952531676504517>❌</emoji> <b>Konnte das"
            " Bild nicht generieren</b>"
        ),
        "drawing": (
            "<emoji document_id=5431456208487716895>🎨</emoji> <b>Zeichne {}"
            " Bild(-er) mit </b><code>{}</code><b>...</b>"
        ),
        "ready": (
            "<emoji document_id=5398001711786762757>✅</emoji> <b>Bild generiert!</b>{}"
        ),
        "debug": (
            "\n\n<i>Modell: {model}, CFG: {cfg}, Schritte: {steps}, Anfrage:"
            " {prompt}, Negative Anfrage: {negative}, {took:.2f}s</i>"
        ),
    }

    strings_tr = {
        "args": (
            "<emoji document_id=5210952531676504517>❌</emoji> <b>Gerekli"
            " argümanlar</b>"
        ),
        "fail": (
            "<emoji document_id=5210952531676504517>❌</emoji> <b>Görüntü"
            " oluşturulamadı</b>"
        ),
        "drawing": (
            "<emoji document_id=5431456208487716895>🎨</emoji> <b>Çiziyorum {}"
            " görüntü(-leri) </b><code>{}</code><b> kullanarak...</b>"
        ),
        "ready": (
            "<emoji document_id=5398001711786762757>✅</emoji> <b>Görüntü"
            " oluşturuldu!</b>{}"
        ),
        "debug": (
            "\n\n<i>Model: {model}, CFG: {cfg}, Adımlar: {steps}, Talep:"
            " {prompt}, Talep reddedildi: {negative}, {took:.2f}s</i>"
        ),
    }

    strings_uz = {
        "args": (
            "<emoji document_id=5210952531676504517>❌</emoji> <b>Talab qilinadi</b>"
        ),
        "fail": (
            "<emoji document_id=5210952531676504517>❌</emoji> <b>Rasm"
            " yaratib bo'lmadi</b>"
        ),
        "drawing": (
            "<emoji document_id=5431456208487716895>🎨</emoji> <b>Rasm(-lar)"
            " chizilmoqda </b><code>{}</code><b> orqali...</b>"
        ),
        "ready": (
            "<emoji document_id=5398001711786762757>✅</emoji> <b>Rasm yaratildi!</b>{}"
        ),
        "debug": (
            "\n\n<i>Model: {model}, CFG: {cfg}, Qadam: {steps}, Talab:"
            " {prompt}, Talab qilinmadi: {negative}, {took:.2f}s</i>"
        ),
    }

    strings_kk = {
        "args": "<emoji document_id=5210952531676504517>❌</emoji> <b>Талап келеді</b>",
        "fail": (
            "<emoji document_id=5210952531676504517>❌</emoji> <b>Сурет"
            " жасап болмады</b>"
        ),
        "drawing": (
            "<emoji document_id=5431456208487716895>🎨</emoji> <b>Сурет(-тер)"
            " жасалуда </b><code>{}</code><b> арқылы...</b>"
        ),
        "ready": (
            "<emoji document_id=5398001711786762757>✅</emoji> <b>Сурет жасалды!</b>{}"
        ),
        "debug": (
            "\n\n<i>Модель: {model}, CFG: {cfg}, Қадам: {steps}, Сұрақ:"
            " {prompt}, Сұрақ жасалмады: {negative}, {took:.2f}s</i>"
        ),
    }

    strings_tt = {
        "args": "<emoji document_id=5210952531676504517>❌</emoji> <b>Талап киләнә</b>",
        "fail": (
            "<emoji document_id=5210952531676504517>❌</emoji> <b>Рәсем ясап"
            " булмады</b>"
        ),
        "drawing": (
            "<emoji document_id=5431456208487716895>🎨</emoji> <b>Рәсем(-ләр)"
            " ясалуда </b><code>{}</code><b> арҗылы...</b>"
        ),
        "ready": (
            "<emoji document_id=5398001711786762757>✅</emoji> <b>Рәсем ясалды!</b>{}"
        ),
        "debug": (
            "\n\n<i>Модель: {model}, CFG: {cfg}, Адым: {steps}, Сорау:"
            " {prompt}, Сорау ясалмады: {negative}, {took:.2f}s</i>"
        ),
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "model",
                "auto",
                "Model to use - For anime characters use Anything-4.5",
                validator=loader.validators.Choice(["auto"]),
            ),
            loader.ConfigValue(
                "steps",
                30,
                "Steps - The higher the number, the more the image will be detailed",
                validator=loader.validators.Integer(minimum=1, maximum=50),
            ),
            loader.ConfigValue(
                "cfg",
                6,
                (
                    "CFG Scale Factor - The higher the number, the more the image will"
                    " follow the prompt"
                ),
                validator=loader.validators.Integer(minimum=1, maximum=20),
            ),
            loader.ConfigValue(
                "sampler",
                "Euler a",
                "Sampler used",
                validator=loader.validators.Choice(
                    ["Euler", "Euler a", "Heun", "DPM++ 2M Karras"]
                ),
            ),
            loader.ConfigValue(
                "debug",
                False,
                "Debug mode",
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "default_negative",
                (
                    "(bad_prompt:0.8), multiple persons, multiple views, extra hands,"
                    " ugly, lowres, bad quality, blurry, disfigured, extra limbs,"
                    " missing limbs, deep fried, cheap art, missing fingers, out of"
                    " frame, cropped, bad art, face hidden, text, speech bubble,"
                    " stretched, bad hands, error, extra digit, fewer digits, worst"
                    " quality, low quality, normal quality, mutated, mutation,"
                    " deformed, severed, dismembered, corpse, pubic, poorly drawn,"
                    " (((deformed hands))), (((more than two hands))), (((deformed"
                    " body))), ((((mutant))))"
                ),
                "Default negative prompt",
            ),
            loader.ConfigValue(
                "default_quantity",
                1,
                "Default quantity of images to generate",
                validator=loader.validators.Integer(minimum=1, maximum=10),
            ),
        )

    async def client_ready(self):
        self._models = json.loads(
            re.search(
                r"VUE_APP_AI_MODELS:'(.*?)',VUE_APP_STATS_STREAMS",
                (
                    await utils.run_sync(
                        requests.get,
                        "https://app.prodia.com"
                        + re.search(
                            (
                                r'defer="defer"'
                                r' src="(\/js\/app\.[^.]*?\.js)"><\/script><link'
                                r' href="\/css'
                            ),
                            (
                                await utils.run_sync(
                                    requests.get,
                                    "https://app.prodia.com/",
                                )
                            ).text,
                        )[1],
                    )
                ).text,
            )[1].replace("\\'", "'")
        )

        self.config._config["model"].validator = loader.validators.Choice(
            ["auto"] + list(self._models.values())
        )

    @loader.command()
    async def draw(self, message: Message):
        """<prompt> [-n <int>] [-comp] [-neg <str>]"""
        if not (args := utils.get_args_raw(message)):
            await utils.answer(message, self.strings("args"))
            return

        negative = ""
        quantity = self.config["default_quantity"]

        if "-n " in args:
            quantity = int(args.split("-n ")[1].split()[0])
            args = args.replace(f"-n {quantity}", "")

        if "-neg" in args:
            args, negative = args.split("-neg")

        comp = False
        if "-comp" in args:
            args = args.replace("-comp", "")
            comp = True

        args, negative = args.strip(), negative.strip()
        if not args:
            await utils.answer(message, self.strings("args"))
            return

        model = (
            next(
                model
                for model in self._models.values()
                if model.startswith("anything-v4.5")
            )
            if self.config["model"] == "auto"
            else self.config["model"]
        )
        message = await utils.answer(
            message,
            self.strings("drawing").format(
                len(self._models) if comp else quantity,
                utils.escape_html("many" if comp else model),
            ),
        )

        images = []

        negative = negative or self.config["default_negative"]
        m = list(self._models.values())

        start = time.time()

        async def create_job():
            return (
                await utils.run_sync(
                    requests.get,
                    "https://arran.fly.dev/generate",
                    params={
                        "prompt": args,
                        "model": m.pop() if comp else model,
                        "negative_prompt": negative,
                        "steps": self.config["steps"],
                        "cfg": self.config["cfg"],
                        "seed": random.randint(0, 1000000),
                        "sampler": self.config["sampler"],
                        "aspect_ratio": "square",
                    },
                )
            ).json()["job"]

        async def create_job_ex():
            try:
                return await create_job()
            except Exception as e:
                logger.error(e)
                await asyncio.sleep(5)
                return await create_job_ex()

        for _ in range(len(m) if comp else quantity):
            job = await create_job_ex()

            q = 0
            while (
                status := (
                    await utils.run_sync(
                        requests.get,
                        f"https://arran.fly.dev/job/{job}",
                    )
                ).json()["status"]
            ) != "succeeded" and q < 20:
                await asyncio.sleep(5)
                q += 1

            if status != "succeeded":
                await utils.answer(message, self.strings("fail"))
                return

            image = io.BytesIO(
                (
                    await utils.run_sync(
                        requests.get,
                        f"https://images.prodia.xyz/{job}.png?download=1",
                        stream=True,
                    )
                ).content
            )
            image.name = "hahahahahhaah.png"

            images.append(image)
            await asyncio.sleep(10)

        await utils.answer_file(
            message,
            images,
            self.strings("ready").format(
                self.strings("debug").format(
                    model=utils.escape_html("many" if comp else model),
                    cfg=self.config["cfg"],
                    steps=self.config["steps"],
                    prompt=utils.escape_html(args),
                    negative=utils.escape_html(negative),
                    took=time.time() - start,
                )
                if self.config["debug"]
                else ""
            ),
        )
