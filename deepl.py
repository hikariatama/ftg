#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://img.icons8.com/external-xnimrodx-lineal-color-xnimrodx/512/000000/external-translate-discussion-xnimrodx-lineal-color-xnimrodx.png
# meta banner: https://mods.hikariatama.ru/badges/deepl.jpg
# meta developer: @hikarimods
# scope: hikka_only
# scope: hikka_min 1.2.10

import logging
import random
import time
import typing

import requests
from telethon.tl.types import Message

from .. import loader, utils


async def translate(text: str, target: str, proxy: dict) -> str:
    a = await utils.run_sync(
        requests.post,
        "https://www2.deepl.com/jsonrpc?method=LMT_handle_jobs",
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
                " like Gecko) Chrome/92.0.4515.131 Safari/537.36"
            ),
            "Content-type": "application/json",
            "Accept": "*/*",
            "Sec-GPC": "1",
            "Origin": "https://www.deepl.com",
            "Sec-Fetch-Site": "same-site",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "https://www.deepl.com/",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9,ru;q=0.8",
        },
        json={
            "jsonrpc": "2.0",
            "method": "LMT_handle_jobs",
            "params": {
                "jobs": [
                    {
                        "kind": "default",
                        "sentences": [{"text": text, "id": 0, "prefix": ""}],
                        "raw_en_context_before": [],
                        "raw_en_context_after": [],
                        "preferred_num_beams": 4,
                        "quality": "fast",
                    }
                ],
                "lang": {
                    "user_preferred_langs": ["EN", "DE", "RU"],
                    "source_lang_user_selected": "auto",
                    "target_lang": target.upper(),
                },
                "priority": -1,
                "commonJobParams": {
                    "regionalVariant": None,
                    "browserType": 1,
                    "formality": None,
                },
                "timestamp": time.time() * 1000,
            },
            "id": random.randint(1000000, 99999999),
        },
        proxies=proxy,
    )

    try:
        return a.json()["result"]["translations"][0]["beams"][0]["sentences"][0]["text"]
    except Exception:
        logger.error(a.text)
        try:
            return f"Error while translating: {a.json()['error']['message']}"
        except Exception:
            return "Error while translating"


logger = logging.getLogger(__name__)


@loader.tds
class DeepLMod(loader.Module):
    """Translates text via DeepL scraping. Proxies are recommended"""

    strings = {
        "name": "DeepLScraper",
        "no_text": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>No text specified</b>"
        ),
        "translated": "🇺🇸 <code>{}</code>",
    }

    strings_ru = {
        "no_text": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Не указан текст</b>"
        ),
        "translated": "🇺🇸 <code>{}</code>",
        "_cmd_doc_deepl": "<text or reply> - Перевести текст через DeepL",
        "_cls_doc": "Переводит текст через DeepL. Рекомендуется использовать прокси",
    }

    strings_de = {
        "no_text": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Kein Text"
            " angegeben</b>"
        ),
        "translated": "🇺🇸 <code>{}</code>",
        "_cmd_doc_deepl": "<Text oder Antwort> - Übersetze Text über DeepL",
        "_cls_doc": (
            "Übersetzt Text über DeepL. Es wird empfohlen, einen Proxy zu verwenden"
        ),
    }

    strings_uz = {
        "no_text": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Matn ko'rsatilmadi</b>"
        ),
        "translated": "🇺🇸 <code>{}</code>",
        "_cmd_doc_deepl": "<matn yoki javob> - DeepL orqali matnni tarjima qilish",
        "_cls_doc": (
            "DeepL orqali matnni tarjima qilish. Proxydan foydalanish maslahat beriladi"
        ),
    }

    strings_hi = {
        "no_text": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>कोई टेक्स्ट नहीं दिया"
            " गया</b>"
        ),
        "translated": "🇺🇸 <code>{}</code>",
        "_cmd_doc_deepl": "<टेक्स्ट या उत्तर> - डीपएल के माध्यम से पाठ का अनुवाद करें",
        "_cls_doc": (
            "डीपएल के माध्यम से पाठ का अनुवाद करता है। प्रॉक्सी का उपयोग करने की सलाह"
            " दी जाती है"
        ),
    }

    strings_tr = {
        "no_text": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Metin belirtilmedi</b>"
        ),
        "translated": "🇺🇸 <code>{}</code>",
        "_cmd_doc_deepl": "<metin veya yanıt> - DeepL ile metni çevir",
        "_cls_doc": "DeepL ile metni çevirir. Proxy kullanmanız önerilir",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue("proxy", "", lambda: "Proxy url")
        )

    async def deeplcmd(self, message: Message):
        """<text or reply> - Translate text via DeepL scraping"""
        args = utils.get_args_raw(message)

        target = (
            "en" if not args or "->" not in args else args[args.find("->") + 2 :][:2]
        )
        args = args.replace(f"->{target}", "")

        reply = await message.get_reply_message()
        if not args and (not reply or not reply.raw_text):
            await utils.answer(message, self.strings("no_text"))
            return

        text = args or reply.raw_text
        await utils.answer(
            message,
            self.strings("translated").format(
                await translate(text, target, {"https": self.config["proxy"]})
            ),
        )
