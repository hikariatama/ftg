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

import logging

from telethon.tl.types import Message

from .. import loader, utils

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
    "<emoji document_id=5226734466315067436>🔤</emoji>",
    "<emoji document_id=5330453760395191684>🔤</emoji>",
    "<emoji document_id=5330523098347218561>🔤</emoji>",
    "<emoji document_id=5361630910816984823>🔤</emoji>",
    "<emoji document_id=5332587336939084375>🔤</emoji>",
    "<emoji document_id=5330369145244491360>🔤</emoji>",
    "<emoji document_id=5361861335812416268>🔤</emoji>",
    "<emoji document_id=5330133162561380231>🔤</emoji>",
    "<emoji document_id=5381808177547321132>🔤</emoji>",
    "<emoji document_id=5330383228442258084>🔤</emoji>",
    "<emoji document_id=5330026574357996347>🔤</emoji>",
    "<emoji document_id=5332396623211274002>🔤</emoji>",
    "<emoji document_id=5332321341024508571>🔤</emoji>",
    "<emoji document_id=5359736027080565026>🔤</emoji>",
    "<emoji document_id=5361583176550457135>🔤</emoji>",
    "<emoji document_id=5361909160273255840>🔤</emoji>",
    "<emoji document_id=5361948540828393629>🔤</emoji>",
    "<emoji document_id=5332514996804918116>🔤</emoji>",
    "<emoji document_id=5332807088940785741>🔤</emoji>",
    "<emoji document_id=5332558333024934589>🔤</emoji>",
    "<emoji document_id=5330069773139059849>🔤</emoji>",
    "<emoji document_id=5393117612416703921>🔤</emoji>",
    "<emoji document_id=5332308237079288987>🔤</emoji>",
    "<emoji document_id=5332575697577714724>🔤</emoji>",
    "<emoji document_id=5332648110726323166>🔤</emoji>",
    "<emoji document_id=5330309934825351007>🔤</emoji>",
    "<emoji document_id=5226734466315067436>🔤</emoji>",
    "<emoji document_id=5330453760395191684>🔤</emoji>",
    "<emoji document_id=5330523098347218561>🔤</emoji>",
    "<emoji document_id=5361630910816984823>🔤</emoji>",
    "<emoji document_id=5332587336939084375>🔤</emoji>",
    "<emoji document_id=5330369145244491360>🔤</emoji>",
    "<emoji document_id=5361861335812416268>🔤</emoji>",
    "<emoji document_id=5330133162561380231>🔤</emoji>",
    "<emoji document_id=5381808177547321132>🔤</emoji>",
    "<emoji document_id=5330383228442258084>🔤</emoji>",
    "<emoji document_id=5330026574357996347>🔤</emoji>",
    "<emoji document_id=5332396623211274002>🔤</emoji>",
    "<emoji document_id=5332321341024508571>🔤</emoji>",
    "<emoji document_id=5359736027080565026>🔤</emoji>",
    "<emoji document_id=5361583176550457135>🔤</emoji>",
    "<emoji document_id=5361909160273255840>🔤</emoji>",
    "<emoji document_id=5361948540828393629>🔤</emoji>",
    "<emoji document_id=5332514996804918116>🔤</emoji>",
    "<emoji document_id=5332807088940785741>🔤</emoji>",
    "<emoji document_id=5332558333024934589>🔤</emoji>",
    "<emoji document_id=5330069773139059849>🔤</emoji>",
    "<emoji document_id=5393117612416703921>🔤</emoji>",
    "<emoji document_id=5332308237079288987>🔤</emoji>",
    "<emoji document_id=5332575697577714724>🔤</emoji>",
    "<emoji document_id=5332648110726323166>🔤</emoji>",
    "<emoji document_id=5330309934825351007>🔤</emoji>",
    "<emoji document_id=5382322671679708881>1️⃣</emoji>",
    "<emoji document_id=5381990043642502553>2️⃣</emoji>",
    "<emoji document_id=5381879959335738545>3️⃣</emoji>",
    "<emoji document_id=5382054253403577563>4️⃣</emoji>",
    "<emoji document_id=5391197405553107640>5️⃣</emoji>",
    "<emoji document_id=5390966190283694453>6️⃣</emoji>",
    "<emoji document_id=5382132232829804982>7️⃣</emoji>",
    "<emoji document_id=5391038994274329680>8️⃣</emoji>",
    "<emoji document_id=5391234698754138414>9️⃣</emoji>",
    "<emoji document_id=5393480373944459905>0️⃣</emoji>",
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
        "_cls_doc": "आपके पाठ को कस्टम इमोजी के रूप में बदलता है। केवल Telegram Premium के लिए",
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
