#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒 Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://img.icons8.com/stickers/344/love-message.png
# meta banner: https://mods.hikariatama.ru/badges/declaration.jpg
# meta developer: @hikarimods
# scope: hikka_only
# scope: hikka_min 1.5.3

import asyncio
import logging
import random
import time

from telethon.tl.types import Message

from .. import loader, utils
from ..inline.types import BotMessage

logger = logging.getLogger(__name__)


@loader.tds
class Declaration(loader.Module):
    """If you are too humble to declare your love, use this module"""

    strings = {
        "name": "Declaration",
        "not_private": (
            "<emoji document_id=6053166094816905153>💀</emoji> <b>This command must be"
            " runned in personal messages...</b>"
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
        "talk": "🫰 Talk",
        "404": "😢 <b>Message has already disappeared. You can't read it now...</b>",
        "read": "🫰 <b>{} has read your declaration</b>",
        "args": (
            "<emoji document_id=6053166094816905153>💀</emoji> <b>Wrong"
            " arguments...</b>"
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
                "🫣 <i>Мой хозяин очень стесняется сказать о чем-то, поэтому он"
                " попросил меня помочь ему...</i>"
            ),
            "🥰 <i>Он просто хотел, чтобы Вы знали, что <b>он любит Вас</b>...</i>",
            "🤗 <i>Это искренние чувства... Пожалуйста, не злитесь на него.</i>",
            "🫶 <i>Лучше скажите ему несколько теплых слов... 🙂</i>",
        ],
        "talk": "🫰 Поговорить",
        "404": "😢 <b>Сообщение уже исчезло. Вы не можете его прочитать...</b>",
        "read": "🫰 <b>{} прочитал ваше признание</b>",
        "args": (
            "<emoji document_id=6053166094816905153>💀</emoji> <b>Неверные"
            " аргументы...</b>"
        ),
    }

    strings_de = {
        "not_private": (
            "<emoji document_id=6053166094816905153>💀</emoji> <b>Diese Befehl muss in"
            " privaten Nachrichten ausgeführt werden...</b>"
        ),
        "ily": (
            "<emoji document_id=5465143921912846619>💭</emoji> <b>Du hast 1 neue"
            ' Nachricht. <a href="https://t.me/{}?start=read_{}">Bitte, lies es</a></b>'
        ),
        "ily_love": [
            "👋 <i>Hallo. Ich bin <b>Hikka</b>.</i>",
            (
                "🫣 <i>Mein Besitzer ist zu bescheiden, um etwas zu sagen, also hat er"
                " mich gebeten, ihm zu helfen...</i>"
            ),
            "🥰 <i>Er wollte nur, dass du weißt, dass <b>er dich liebt</b>...</i>",
            "🤗 <i>Das sind ehrliche Gefühle... Bitte, verzeih ihm.</i>",
            "🫶 <i>Sag ihm besser ein paar warme Worte... 🙂</i>",
        ],
        "talk": "🫰 Reden",
        "404": (
            "😢 <b>Die Nachricht ist bereits verschwunden. Du kannst sie jetzt nicht"
            " lesen...</b>"
        ),
        "read": "🫰 <b>{} hat dein Geständnis gelesen</b>",
        "args": (
            "<emoji document_id=6053166094816905153>💀</emoji> <b>Falsche"
            " Argumente...</b>"
        ),
    }

    strings_hi = {
        "not_private": (
            "<emoji document_id=6053166094816905153>💀</emoji> <b>यह कमांड निजी"
            " संदेशों में चलाए जाने चाहिए...</b>"
        ),
        "ily": (
            "<emoji document_id=5465143921912846619>💭</emoji> <b>आपके पास 1 नया संदेश"
            ' है। <a href="https://t.me/{}?start=read_{}">कृपया, उसे पढ़ें</a></b>'
        ),
        "ily_love": [
            "👋 <i>नमस्ते। मैं <b>हिक्का</b> हूँ।</i>",
            (
                "🫣 <i>मेरे मालिक को कुछ कहने के लिए बहुत बारीच है, इसलिए उन्होंने"
                " मुझे उनकी मदद करने के लिए कहा...</i>"
            ),
            "🥰 <i>उसने आपको सिर्फ यह बताना चाहता था कि <b>वह आपको पसंद करता है</b>...</i>",
            "🤗 <i>ये सच्चे भावनाएं हैं... कृपया उसे माफ़ करें।</i>",
            "🫶 <i>उसे बेहतर शब्दों के साथ बोलें... 🙂</i>",
        ],
        "talk": "🫰 बात करना",
        "404": "😢 <b>संदेश पहले ही नष्ट हो गया है। आप इसे अब पढ़ नहीं सकते...</b>",
        "read": "🫰 <b>आपने {} के लिए अपना प्रार्थना पढ़ा</b>",
        "args": "<emoji document_id=6053166094816905153>💀</emoji> <b>गलत तर्क...</b>",
    }

    strings_tr = {
        "not_private": (
            "<emoji document_id=6053166094816905153>💀</emoji> <b>Bu komut özel"
            " mesajlarda çalıştırılmalıdır...</b>"
        ),
        "ily": (
            "<emoji document_id=5465143921912846619>💭</emoji> <b>Yeni 1 mesajınız var."
            ' <a href="https://t.me/{}?start=read_{}">Lütfen, okuyun</a></b>'
        ),
        "ily_love": [
            "👋 <i>Merhaba. Ben <b>Hikka</b>.</i>",
            "🫣 <i>Sahibim bir şey söylemekten çekinince, yardım etmeme söyledi...</i>",
            "🥰 <i>Sadece ona <b>seni sevdiğini</b> söylemek istedi...</i>",
            "🤗 <i>Bu gerçek duygular... Lütfen, affet.</i>",
            "🫶 <i>Bunu ona daha iyi söyle... 🙂</i>",
        ],
        "talk": "🫰 Konuş",
        "404": "😢 <b>Mesaj zaten kaybolmuş. Okuyamazsın...</b>",
        "read": "🫰 <b>{} senin itirafını okudu</b>",
        "args": (
            "<emoji document_id=6053166094816905153>💀</emoji> <b>Yanlış argüman...</b>"
        ),
    }

    strings_ja = {
        "not_private": (
            "<emoji document_id=6053166094816905153>💀</emoji> <b>このコマンドはプライベート"
            " メッセージで実行される必要があります...</b>"
        ),
        "ily": (
            "<emoji document_id=5465143921912846619>💭</emoji>"
            " <b>新しい1つのメッセージがあります。"
            ' <a href="https://t.me/{}?start=read_{}">読んでください</a></b>'
        ),
        "ily_love": [
            "👋 <i>こんにちは。 私は<b>ヒッカ</b>です。</i>",
            "🫣 <i>主人が何か言いたくないので、助けてほしいと言った...</i>",
            "🥰 <i>彼はただ<b>あなたを愛している</b>と言いたかった...</i>",
            "🤗 <i>これは本当の感情です... 許してください。</i>",
            "🫶 <i>もっと良い言葉で言ってください... 🙂</i>",
        ],
        "talk": "🫰 会話",
        "404": (
            "😢 <b>メッセージはすでに消えています。"
            " あなたはそれを読むことはできません...</b>"
        ),
        "read": "🫰 <b>{}はあなたの告白を読みました</b>",
        "args": (
            "<emoji document_id=6053166094816905153>💀</emoji> <b>間違った引数...</b>"
        ),
    }

    strings_kr = {
        "not_private": (
            "<emoji document_id=6053166094816905153>💀</emoji> <b>이 명령은 개인"
            " 메시지에서 실행되어야합니다...</b>"
        ),
        "ily": (
            "<emoji document_id=5465143921912846619>💭</emoji> <b>새로운 메시지가 있습니다."
            ' <a href="https://t.me/{}?start=read_{}">읽어주세요</a></b>'
        ),
        "ily_love": [
            "👋 <i>안녕하세요. 나는 <b>히카</b>입니다.</i>",
            "🫣 <i>주인이 무언가를 말하고 싶지 않아서 도움을 요청했습니다...</i>",
            "🥰 <i>그저 그에게 <b>너를 사랑한다</b>고 말하고 싶었습니다...</i>",
            "🤗 <i>이것은 진짜 감정입니다... 용서해주세요.</i>",
            "🫶 <i>더 좋은 말로 말하세요... 🙂</i>",
        ],
        "talk": "🫰 대화",
        "404": "😢 <b>메시지는 이미 삭제되었습니다. 읽을 수 없습니다...</b>",
        "read": "🫰 <b>{} 당신의 고백을 읽었습니다</b>",
        "args": (
            "<emoji document_id=6053166094816905153>💀</emoji> <b>잘못된 인수...</b>"
        ),
    }

    strings_ar = {
        "not_private": (
            "<emoji document_id=6053166094816905153>💀</emoji> <b>هذا الأمر يجب أن يتم"
            " تنفيذه في رسالة خاصة...</b>"
        ),
        "ily": (
            "<emoji document_id=5465143921912846619>💭</emoji> <b>هناك رسالة جديدة."
            ' <a href="https://t.me/{}?start=read_{}">اقرأ</a></b>'
        ),
        "ily_love": [
            "👋 <i>مرحبا. أنا <b>هيكا</b>.</i>",
            "🫣 <i>طلب المالك مساعدة لأنه لا يريد أن يقول شيئا...</i>",
            "🥰 <i>أراد فقط أن يقول له <b>أنا أحبك</b>...</i>",
            "🤗 <i>هذه حقيقة العواطف... يرجى التكرم.</i>",
            "🫶 <i>قلها بطريقة أفضل... 🙂</i>",
        ],
        "talk": "🫰 محادثة",
        "404": "😢 <b>تم حذف الرسالة بالفعل. لا يمكن قراءتها...</b>",
        "read": "🫰 <b>{} قرأت إعترافك</b>",
        "args": (
            "<emoji document_id=6053166094816905153>💀</emoji> <b>وسيطغير صالح...</b>"
        ),
    }

    strings_es = {
        "not_private": (
            "<emoji document_id=6053166094816905153>💀</emoji> <b>Este comando debe"
            " ejecutarse en mensaje privado...</b>"
        ),
        "ily": (
            "<emoji document_id=5465143921912846619>💭</emoji> <b>Tienes un nuevo"
            ' mensaje. <a href="https://t.me/{}?start=read_{}">Lee</a></b>'
        ),
        "ily_love": [
            "👋 <i>Hola. Soy <b>Hika</b>.</i>",
            "🫣 <i>El dueño solicitó ayuda porque no quería decir nada...</i>",
            "🥰 <i>Simplemente quería decirle <b>te amo</b>...</i>",
            "🤗 <i>Esto es real... Por favor perdóname.</i>",
            "🫶 <i>Dilo mejor... 🙂</i>",
        ],
        "talk": "🫰 Conversación",
        "404": "😢 <b>El mensaje ya ha sido eliminado. No se puede leer...</b>",
        "read": "🫰 <b>{} leyó tu confesión</b>",
        "args": (
            "<emoji document_id=6053166094816905153>💀</emoji> <b>Argumento"
            "no válido...</b>"
        ),
    }

    async def client_ready(self):
        self.ids = self.pointer("declarations", {})

    @loader.command(ru_doc="Признаться в любви")
    async def declare(self, message: Message):
        """Declare love"""
        if not message.is_private:
            await utils.answer(message, self.strings("not_private"))
            return

        id_ = utils.rand(8)
        await utils.answer(
            message,
            self.strings("ily").format(self.inline.bot_username, id_),
        )
        self.ids[id_] = int(time.time()) + 24 * 60 * 60

    async def aiogram_watcher(self, message: BotMessage):
        if not message.text.startswith("/start read_"):
            return

        for id_, info in self.ids.copy().items():
            if info < int(time.time()):
                self.ids.pop(id_)
                continue

        id_ = message.text.split("_")[1]
        if id_ not in self.ids:
            await message.answer(self.strings("404"))
            return

        info = self.ids.pop(id_)
        for m in self.strings("ily_love")[:-1]:
            await message.answer(m)
            await asyncio.sleep(random.randint(350, 400) / 100)

        await self.inline.bot.send_message(
            self._client.tg_id,
            self.strings("read").format(
                utils.escape_html(message.from_user.full_name),
            ),
        )

        await message.answer(
            self.strings("ily_love")[-1],
            reply_markup=self.inline.generate_markup(
                {
                    "text": self.strings("talk"),
                    "url": f"tg://user?id={self._client.tg_id}",
                }
            ),
        )
