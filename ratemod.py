#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# scope: hikka_min 1.2.10

# meta pic: https://img.icons8.com/external-phatplus-lineal-color-phatplus/512/000000/external-rate-email-phatplus-lineal-color-phatplus.png
# meta developer: @hikarimods

import asyncio
import hashlib
import re

import requests
from telethon.tl.types import Message

from .. import loader, utils


@loader.tds
class RateModuleMod(loader.Module):
    """Rates module and suggests fixes"""

    strings = {
        "name": "RateMod",
        "template": (
            "👮‍♂️ <b>Mode rating </b><code>{}</code><b>:</b>\n{} {} <b>[{}]</b>\n\n{}"
        ),
        "no_file": "<b>What should I check?... 🗿</b>",
        "cannot_check_file": "<b>Check error</b>",
    }

    strings_ru = {
        "template": (
            "👮‍♂️ <b>Оценка модуля </b><code>{}</code><b>:</b>\n{} {} <b>[{}]</b>\n\n{}"
        ),
        "no_file": "<b>А что проверять то?... 🗿</b>",
        "cannot_check_file": "<b>Ошибка проверки</b>",
        "_cmd_doc_ratemod": "<код> - Оценить модуль",
        "_cls_doc": "Оценивает модуль и дает рекомендации",
    }

    @loader.unrestricted
    async def ratemodcmd(self, message: Message):
        """<reply_to_file|file|link> - Rate code"""
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        if (
            not reply
            and not getattr(reply, "media", None)
            and not getattr(message, "media", None)
            and not args
            and not utils.check_url(args)
        ):
            return await utils.answer(message, self.strings("no_file"))

        checking = (
            getattr(reply, "media", None)
            if getattr(reply, "media", None) is not None
            else (
                getattr(message, "media", None)
                if getattr(message, "media", None) is not None
                else (args if args and utils.check_url(args) else 0)
            )
        )
        if type(checking) is int:
            return await utils.answer(message, self.strings("no_file"))

        if type(checking) is not str:
            try:
                file = await self._client.download_file(
                    getattr(reply, "media", None)
                    if getattr(reply, "media", None) is not None
                    else getattr(message, "media", None),
                    bytes,
                )
            except Exception:
                return await utils.answer(
                    message,
                    self.strings("cannot_check_file"),
                )

            try:
                code = file.decode("utf-8").replace("\r\n", "\n")
            except Exception:
                return await utils.answer(
                    message,
                    self.strings("cannot_check_file"),
                )

        else:
            try:
                code = (await utils.run_sync(requests.get, args)).text
            except Exception:
                return await utils.answer(message, self.strings("cannot_check_file"))

        try:
            mod_name = re.search(
                r"""strings[ ]*=[ ]*{.*?name['"]:[ ]*['"](.*?)['"]""", code, flags=re.S
            ).group(1)
        except Exception:
            mod_name = "Unknown"

        import_regex = [
            r"^[^#]rom ([^\n\r]*) import [^\n\r]*$",
            r"^[^#]mport ([^\n\r]*)[^\n\r]*$",
            r"""__import__[(]['"]([^'"]*)['"][)]""",
        ]
        imports = [
            re.findall(import_re, code, flags=re.M | re.DOTALL)
            for import_re in import_regex
        ]

        if ".." in imports:
            del imports[imports.index("..")]

        splitted = [
            _
            for _ in list(
                zip(
                    list(
                        map(
                            lambda x: len(re.findall(r"[ \t]+(if|elif|else).+:", x)),
                            re.split(r"[ \t]*async def .*?cmd\(", code),
                        )
                    ),
                    [""] + re.findall(r"[ \t]*async def (.*?)cmd\(", code),
                )
            )
            if _[0] > 10
        ]

        comments = ""

        score = 4.6
        if len(imports) > 10:
            comments += (
                f"🔻 <code>{{-0.1}}</code> <b>A lot of imports ({len(imports)})"
                " </b><i>[memory]</i>\n"
            )
            score -= 0.1
        if "requests" in imports and "utils.run_sync" not in code:
            comments += (
                "🔻 <code>{-0.5}</code> <b>Sync requests</b> <i>[blocks runtime]</i>\n"
            )
            score -= 0.5
        if "while True" in code or "while 1" in code:
            comments += (
                "🔻 <code>{-0.1}</code> <b>While true</b> <i>[block runtime*]</i>\n"
            )
            score -= 0.1
        if ".edit(" in code:
            comments += (
                "🔻 <code>{-0.3}</code> <b>Classic message.edit</b> <i>[no twink"
                " support]</i>\n"
            )
            score -= 0.3
        if re.search(r"@.*?[bB][oO][tT]", code) is not None:
            bots = " | ".join(re.findall(r"@.*?[bB][oO][tT]", code))
            comments += (
                f"🔻 <code>{{-0.2}}</code> <b>Bot-abuse (</b><code>{bots}</code><b>)</b>"
                " <i>[module will die some day]</i>\n"
            )
            score -= 0.2
        if re.search(r'[ \t]+async def .*?cmd.*\n[ \t]+[^\'" \t]', code) is not None:
            undoc = " | ".join(
                list(re.findall(r'[ \t]+async def (.*?)cmd.*\n[ \t]+[^" \t]', code))
            )

            comments += (
                f"🔻 <code>{{-0.4}}</code> <b>No docs (</b><code>{undoc}</code><b>)</b>"
                " <i>[all commands must be documented]</i>\n"
            )
            score -= 0.4
        if "time.sleep" in code or "from time import sleep" in code:
            comments += (
                "🔻 <code>{-2.0}</code> <b>Sync sleep (</b><code>time.sleep</code><b>)"
                " replace with (</b><code>await asyncio.sleep</code><b>)</b> <i>[blocks"
                " runtime]</i>\n"
            )
            score -= 2
        if [_ for _ in code.split("\n") if len(_) > 300]:
            ll = max(len(_) for _ in code.split("\n") if len(_) > 300)
            comments += (
                f"🔻 <code>{{-0.1}}</code> <b>Long lines ({ll})</b> <i>[PEP"
                " violation]</i>\n"
            )
            score -= 0.1
        if re.search(r'[\'"] ?\+ ?.*? ?\+ ?[\'"]', code) is not None:
            comments += (
                "🔻 <code>{-0.1}</code> <b>Avoiding f-строк</b> <i>[causes"
                " problems]</i>\n"
            )
            score -= 0.1
        if splitted:
            comments += (
                "🔻 <code>{-0.2}</code> <b>Big 'if' trees"
                f" (</b><code>{' | '.join([f'{chain} в {fun}' for chain, fun in splitted])}</code><b>)</b>"
                " <i>[readability]</i>\n"
            )
            score -= 0.2
        if "== None" in code or "==None" in code:
            comments += (
                "🔻 <code>{-0.3}</code> <b>Type comparsation via ==</b> <i>[google"
                " it]</i>\n"
            )

            score -= 0.3
        if "is not None else" in code:
            comments += (
                "🔻 <code>{-0.1}</code> <b>Unneccessary ternary operator usage"
                " (</b><code>if some_var is not None else another</code> <b>-></b>"
                " <code>some_var or another</code><b>)</b> <i>[readability]</i>\n"
            )

            score -= 0.1
        if "utils.answer" in code and ".edit(" not in code:
            comments += (
                "🔸 <code>{+0.3}</code> <b>utils.answer</b> <i>[twinks support]</i>\n"
            )
            score += 0.3
        if re.search(r'[ \t]+async def .*?cmd.*\n[ \t]+[^\'" \t]', code) is None:
            comments += (
                "🔸 <code>{+0.3}</code> <b>Docs</b> <i>[all commands are"
                " documented]</i>\n"
            )
            score += 0.3
        if "requests" in imports and "utils.run_sync" in code or "aiohttp" in imports:
            comments += (
                "🔸 <code>{+0.3}</code> <b>Async requests</b> <i>[do not stop"
                " runtime]</i>\n"
            )
            score += 0.3

        api_endpoint = "https://mods.hikariatama.ru/check?hash="
        sha1 = hashlib.sha1()
        sha1.update(code.encode("utf-8"))
        try:
            check_res = (
                await utils.run_sync(requests.get, api_endpoint + str(sha1.hexdigest()))
            ).text
        except Exception:
            check_res = ""

        if check_res in {"yes", "db"}:
            comments += (
                "🔸 <code>{+1.0}</code> <b>Module is verified</b> <i>[no scam]</i>\n"
            )
            score += 1.0

        score = round(score, 1)

        score = min(score, 5.0)
        await utils.answer(
            message,
            self.strings("template").format(
                mod_name,
                "⭐️" * round(score),
                score,
                ["Shit", "Bad", "Poor", "Normal", "Ok", "Good"][round(score)],
                comments,
            ),
        )
