#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://img.icons8.com/plasticine/344/hiragana-ma.png
# meta developer: @hikarimods
# meta banner: https://mods.hikariatama.ru/badges/alphabet.jpg
# scope: hikka_only
# scope: hikka_min 1.4.0

from .. import loader, utils
from telethon.tl.types import Message
import logging

logger = logging.getLogger(__name__)

to_ = [
    '<emoji document_id="5456128055414103034">😀</emoji>',
    '<emoji document_id="5456434780503548020">😀</emoji>',
    '<emoji document_id="5456256891548081456">😀</emoji>',
    '<emoji document_id="5454330491341643548">😀</emoji>',
    '<emoji document_id="5456670806136332319">😀</emoji>',
    '<emoji document_id="5456638048420767252">😀</emoji>',
    '<emoji document_id="5456546939279514692">😀</emoji>',
    '<emoji document_id="5454311039434759616">😀</emoji>',
    '<emoji document_id="5456509650373451167">😀</emoji>',
    '<emoji document_id="5456623527136336113">😀</emoji>',
    '<emoji document_id="5456505132067855523">😀</emoji>',
    '<emoji document_id="5456371910772269309">😀</emoji>',
    '<emoji document_id="5456140738452528837">😀</emoji>',
    '<emoji document_id="5453930556871941888">😀</emoji>',
    '<emoji document_id="5453937347215238994">😀</emoji>',
    '<emoji document_id="5456502344634079449">😀</emoji>',
    '<emoji document_id="5456402237536346480">😀</emoji>',
    '<emoji document_id="5456119517019119748">😀</emoji>',
    '<emoji document_id="5456490688092838489">😀</emoji>',
    '<emoji document_id="5456151875302726462">😀</emoji>',
    '<emoji document_id="5454053289857393595">😀</emoji>',
    '<emoji document_id="5454338918067479229">😀</emoji>',
    '<emoji document_id="5454359744363895908">😀</emoji>',
    '<emoji document_id="5454131191974207370">😀</emoji>',
    '<emoji document_id="5456480702293877170">😀</emoji>',
    '<emoji document_id="5454080962331680684">😀</emoji>',
    '<emoji document_id="5456518863078301519">😀</emoji>',
    '<emoji document_id="5454347190174490271">😀</emoji>',
    '<emoji document_id="5453878587767660028">😀</emoji>',
    '<emoji document_id="5454343273164316651">😀</emoji>',
    '<emoji document_id="5456437748325948254">😀</emoji>',
    '<emoji document_id="5454207307384626821">😀</emoji>',
    '<emoji document_id="5454275588774699252">😀</emoji>',
    '<emoji document_id="5456128055414103034">😀</emoji>',
    '<emoji document_id="5456434780503548020">😀</emoji>',
    '<emoji document_id="5456256891548081456">😀</emoji>',
    '<emoji document_id="5454330491341643548">😀</emoji>',
    '<emoji document_id="5456670806136332319">😀</emoji>',
    '<emoji document_id="5456638048420767252">😀</emoji>',
    '<emoji document_id="5456546939279514692">😀</emoji>',
    '<emoji document_id="5454311039434759616">😀</emoji>',
    '<emoji document_id="5456509650373451167">😀</emoji>',
    '<emoji document_id="5456623527136336113">😀</emoji>',
    '<emoji document_id="5456505132067855523">😀</emoji>',
    '<emoji document_id="5456371910772269309">😀</emoji>',
    '<emoji document_id="5456140738452528837">😀</emoji>',
    '<emoji document_id="5453930556871941888">😀</emoji>',
    '<emoji document_id="5453937347215238994">😀</emoji>',
    '<emoji document_id="5456502344634079449">😀</emoji>',
    '<emoji document_id="5456402237536346480">😀</emoji>',
    '<emoji document_id="5456119517019119748">😀</emoji>',
    '<emoji document_id="5456490688092838489">😀</emoji>',
    '<emoji document_id="5456151875302726462">😀</emoji>',
    '<emoji document_id="5454053289857393595">😀</emoji>',
    '<emoji document_id="5454338918067479229">😀</emoji>',
    '<emoji document_id="5454359744363895908">😀</emoji>',
    '<emoji document_id="5454131191974207370">😀</emoji>',
    '<emoji document_id="5456480702293877170">😀</emoji>',
    '<emoji document_id="5454080962331680684">😀</emoji>',
    '<emoji document_id="5456518863078301519">😀</emoji>',
    '<emoji document_id="5454347190174490271">😀</emoji>',
    '<emoji document_id="5453878587767660028">😀</emoji>',
    '<emoji document_id="5454343273164316651">😀</emoji>',
    '<emoji document_id="5456437748325948254">😀</emoji>',
    '<emoji document_id="5454207307384626821">😀</emoji>',
    '<emoji document_id="5454275588774699252">😀</emoji>',
    '<emoji document_id="6030739996095286579">📝</emoji>',
    '<emoji document_id="6030689461510082519">📝</emoji>',
    '<emoji document_id="6033012162643888864">📝</emoji>',
    '<emoji document_id="6033118269810936920">📝</emoji>',
    '<emoji document_id="6030380674836335648">📝</emoji>',
    '<emoji document_id="6030372557348146420">📝</emoji>',
    '<emoji document_id="6032678473749761092">📝</emoji>',
    '<emoji document_id="6032750852538633161">📝</emoji>',
    '<emoji document_id="6030779655823297970">📝</emoji>',
    '<emoji document_id="6032658631000854452">📝</emoji>',
    '<emoji document_id="6033106823723093634">📝</emoji>',
    '<emoji document_id="6033022951601736655">📝</emoji>',
    '<emoji document_id="6032931765151075341">📝</emoji>',
    '<emoji document_id="6033044984783965208">📝</emoji>',
    '<emoji document_id="6033017376734186738">📝</emoji>',
    '<emoji document_id="6032902623797972103">📝</emoji>',
    '<emoji document_id="6032902164236471239">📝</emoji>',
    '<emoji document_id="6030663373878725803">📝</emoji>',
    '<emoji document_id="6032779856452782933">📝</emoji>',
    '<emoji document_id="6032669651886935022">📝</emoji>',
    '<emoji document_id="6032973486463388995">📝</emoji>',
    '<emoji document_id="6032713988834332099">📝</emoji>',
    '<emoji document_id="6030348458286648381">📝</emoji>',
    '<emoji document_id="6030414287250393828">📝</emoji>',
    '<emoji document_id="6032794729924529597">📝</emoji>',
    '<emoji document_id="6032874534711856088">📝</emoji>',
    '<emoji document_id="6033031399802408686">📝</emoji>',
    '<emoji document_id="6033104066354088714">📝</emoji>',
    '<emoji document_id="6030880269727173905">📝</emoji>',
    '<emoji document_id="6032766619363577074">📝</emoji>',
    '<emoji document_id="6030470899214322593">📝</emoji>',
    '<emoji document_id="6030376521602960830">📝</emoji>',
    '<emoji document_id="6030708522574941667">📝</emoji>',
    '<emoji document_id="6030750630434310932">📝</emoji>',
    '<emoji document_id="6032984777932410105">📝</emoji>',
    '<emoji document_id="6032852243831590121">📝</emoji>',
    '<emoji document_id="6032613495189539415">📝</emoji>',
    '<emoji document_id="6030593164048337780">📝</emoji>',
    '<emoji document_id="6030374601752579421">📝</emoji>',
    '<emoji document_id="6033012008025067358">📝</emoji>',
    '<emoji document_id="6030824366432849413">📝</emoji>',
    '<emoji document_id="6030545885048343757">📝</emoji>',
    '<emoji document_id="6033056722929585373">📝</emoji>',
    '<emoji document_id="6030717868423777346">📝</emoji>',
    '<emoji document_id="6032714843532823639">📝</emoji>',
    '<emoji document_id="6033116620543495287">📝</emoji>',
    '<emoji document_id="6033123896218094530">📝</emoji>',
    '<emoji document_id="6030359290194169552">📝</emoji>',
    '<emoji document_id="6030541495591767119">📝</emoji>',
    '<emoji document_id="6030408175511932773">📝</emoji>',
    '<emoji document_id="6032906828570954767">📝</emoji>',
    '<emoji document_id="6030434568085966278">📝</emoji>',
    '<emoji document_id="6035077578056797187">1⃣</emoji>',
    '<emoji document_id="6035333132905876080">2⃣</emoji>',
    '<emoji document_id="6032895330943503887">3⃣</emoji>',
    '<emoji document_id="6032721217264291023">4⃣</emoji>',
    '<emoji document_id="6032673431458156049">5⃣</emoji>',
    '<emoji document_id="6034985489663003154">6⃣</emoji>',
    '<emoji document_id="6035130569363295212">7⃣</emoji>',
    '<emoji document_id="6032603363361688717">8⃣</emoji>',
    '<emoji document_id="6032688352174542779">9⃣</emoji>',
    '<emoji document_id="6032752080899280021">0⃣</emoji>',
    '<emoji document_id="6035271044858645168">📝</emoji>',
    '<emoji document_id="6034823612345617299">📝</emoji>',
    '<emoji document_id="6032617102962069967">⭕️</emoji>',
    '<emoji document_id="6032933036461395383">🛑</emoji>',
    '<emoji document_id="6033101201610903072">❗️</emoji>',
    '<emoji document_id="6033056731519519862">❓</emoji>',
    '<emoji document_id="6032769737509833594">📛</emoji>',
]

from_ = (
    "абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890().,!? "
)


@loader.tds
class Alphabet(loader.Module):
    """Replaces your text with custom emojis. Telegram Premium only"""

    strings = {
        "name": "Alphabet",
        "no_text": "🚫 <b>Specify text to replace</b>",
        "premium_only": (
            "⭐️ This module is available only to Telegram Premium subscribers"
        ),
    }
    strings_ru = {
        "no_text": "🚫 <b>Укажите текст для замены</b>",
        "premium_only": "⭐️ Этот модуль доступен только для Telegram Premium",
        "_cmd_doc_a": "Заменить текст на эмодзи",
        "_cls_doc": "Заменяет текст на кастомные эмодзи. Только для Telegram Premium",
    }
    strings_de = {
        "no_text": "🚫 <b>Gib den Text ein, der ersetzt werden soll</b>",
        "premium_only": (
            "⭐️ Dieses Modul ist nur für Telegram Premium-Abonnenten verfügbar"
        ),
        "_cmd_doc_a": "Ersetze Text durch Emojis",
        "_cls_doc": (
            "Ersetzt Text durch benutzerdefinierte Emojis. Nur für Telegram Premium"
        ),
    }
    strings_hi = {
        "no_text": "🚫 <b>बदलने के लिए पाठ निर्दिष्ट करें</b>",
        "premium_only": "⭐️ यह मॉड्यूल केवल Telegram Premium सदस्यों के लिए उपलब्ध है",
        "_cmd_doc_a": "पाठ को इमोजी के रूप में बदलें",
        "_cls_doc": (
            "आपके पाठ को कस्टम इमोजी के रूप में बदलता है। केवल Telegram Premium के लिए"
        ),
    }
    strings_uz = {
        "no_text": "🚫 <b>Almashtirish uchun matn belgilang</b>",
        "premium_only": (
            "⭐️ Bu modul faqat Telegram Premium obuna bo'lganlar uchun mavjud"
        ),
        "_cmd_doc_a": "Matnni emoji bilan almashtiring",
        "_cls_doc": (
            "Matnni sizning emojiingiz bilan almashtiradi. Faqat Telegram Premium uchun"
        ),
    }

    async def client_ready(self):
        if not (await self._client.get_me()).premium:
            raise loader.LoadError(self.strings("premium_only"))

        self._from = from_
        self._to = to_

    async def acmd(self, message: Message):
        """<text> - Write text with emojis"""
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        if not args and not reply:
            await utils.answer(message, self.strings("no_text"))
            return

        await utils.answer(
            message,
            "".join(
                to_[from_.index(char)] if char in from_ else char
                for char in args or reply.raw_text
            ),
        )
