# █ █ ▀ █▄▀ ▄▀█ █▀█ ▀    ▄▀█ ▀█▀ ▄▀█ █▀▄▀█ ▄▀█
# █▀█ █ █ █ █▀█ █▀▄ █ ▄  █▀█  █  █▀█ █ ▀ █ █▀█
#
#              © Copyright 2022
#
#          https://t.me/hikariatama
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://img.icons8.com/stickers/500/000000/cards.png
# meta developer: @hikariatama

import asyncio
import io
import json
import re
from random import randint

from telethon.tl.types import Message

from .. import loader, utils

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
    <title>Testing ^title_deck_name^</title>
    <style type="text/css">
        @import url('https://fonts.googleapis.com/css2?family=Exo+2&display=swap');
        * {
            box-sizing: border-box;
            transition: all .3s ease;
        }
        body {
            width: 100%;
            height: 100%;
            padding: 0;
            margin: 0;
            background: #121212;
            color: #fff;
            font-family: 'Exo 2';
        }

        .cards, .testing {
            width: 94%;
            margin-left: 3%;
            min-height: 30vh;
            background: #121212;
            border-radius: 10px;
            box-shadow: inset 9.31px 9.31px 19px #0B0B0B, inset -9.31px -9.31px 19px #161616;
            padding: 15px 20px;
        }

        .button {
            width: 94%;
            padding: 20px 0;
            text-align: center;
            font-size: 22px;
            margin-left: 3%;
            background: #121212;
            border-radius: 10px;
            margin-top: 10px;
            user-select: none;
            cursor: pointer;
            box-shadow: inset 9.31px 9.31px 19px #0B0B0B, inset -9.31px -9.31px 19px #161616;
        }

        .back {
            width: 94%;
            border: none;
            outline: none;
            padding: 10px 0;
            text-align: center;
            font-size: 20px;
            margin-left: 3%;
            border-radius: 5px;
            margin-top: 10px;

            background: linear-gradient(145deg , #d9d9d9, #C8C8C8);
            box-shadow: rgb(117 117 117) 0px 1px 20px 0px inset;
        }

        .back::placeholder {
            color: #555;
        }

        h1 {
            margin: 20px;
            text-align: center;
            font-size: 25px;
            padding: 0;
            margin-left: 5%;
        }

        @media screen and (max-width: 736px) {
            body {
                padding: 10px;
            }

            h1 {
                font-size: 25px;
                text-align: center;
                margin-top: 10px;
                margin-bottom: 20px;
            }
        }

        .testing {
            display: none;
        }

        .front {
            margin-left: 0;
            margin-right: 0;
        }
    </style>
</head>
<body>
    <h1>^deck_name^</h1>
    <div class="cards">
        Loading...
    </div>
    <div class="testing">
        <h1 class="front"></h1>
        <input class="back" type="text" placeholder="Ответ">
    </div>
    <div class="begin button">Start test</div>

    <script type="text/javascript">
        cards = JSON.parse("^json_cards^");
        var cards_html = "";
        for (var front in cards) {
            cards_html += front + " - " + cards[front] + "<br>\\n";
        }

        document.querySelector('.cards').innerHTML = cards_html;

        function getRndInteger(min, max) {return Math.floor(Math.random() * (max - min) ) + min;}

        function render_next_one() {
            var keys = Object.keys(cards);
            var front = keys[getRndInteger(0,keys.length)];
            var back = cards[front];
            document.querySelector('.front').innerHTML = front;
            document.querySelector('.back').setAttribute('answer', back);
        }

        function check_answer() {
            var el = document.querySelector('.back');
            if(el.getAttribute('answer') == el.value){
                document.querySelector('.front').innerHTML = "Yup!";
                document.querySelector('.testing').style.background = '#26681e';
            } else {
                document.querySelector('.testing').style.background = '#611a1a';
                document.querySelector('.front').innerHTML = "Nope. Right answer: " + el.getAttribute('answer');
            }

            setTimeout(() => {
                document.querySelector('.testing').style.background = '#121212';
                render_next_one();
            }, 1000);
            el.value = "";
        }

        document.querySelector('.begin').onclick = function() {
            document.querySelector('.cards').style.opacity = 0;
            setTimeout(() => {document.querySelector('.cards').style.display = 'none'; document.querySelector('.testing').style.display = 'block';}, 300);
            this.classList.remove('begin');
            this.classList.add('next');
            this.innerHTML = "Check answer";
            render_next_one();
            document.querySelector('.next').onclick = function() {
                check_answer();
            }
        }

        document.querySelector('.back').onkeyup = function(e) {
            if (e.key === 'Enter' || e.keyCode === 13) {
                check_answer();
            }
        }
    </script>
</body>
</html>
        """


@loader.tds
class FlashCardsMod(loader.Module):
    """Flash cards for learning"""

    strings = {
        "name": "FlashCards",
        "deck_not_found": "<b>🚫 Deck not found</b",
        "no_deck_name": "<b>You haven't provided deck name</b>",
        "deck_created": "#Deck <code>#{}</code> <b>{}</b> successfully created!",
        "deck_removed": "<b>🚫 Deck removed</b>",
        "save_deck_no_reply": "<b>🚫 This command should be used in reply to message with deck items.</b>",
        "deck_saved": "✅ <b>Deck saved!</b>",
        "generating_page": "<b>⚙️ Generating page, please wait ...</b>",
        "offline_testing": "<b>📖 Offline testing, based on deck {}</b>",
    }

    strings_ru = {
        "deck_not_found": "<b>🚫 Дека не найдена</b",
        "no_deck_name": "<b>Ты не указал имя деки</b>",
        "deck_created": "#Deck <code>#{}</code> <b>{}</b> успешно создана!",
        "deck_removed": "<b>🚫 Дека удалена</b>",
        "save_deck_no_reply": "<b>🚫 Эта команда должна выполняться в ответ на измененную деку.</b>",
        "deck_saved": "✅ <b>Дека сохранена!</b>",
        "generating_page": "<b>⚙️ Генерирую страницу, секунду...</b>",
        "offline_testing": "<b>📖 Оффлайн тестирование на основе деки {}</b>",
        "_cmd_doc_newdeck": "<name> - Создать новую деку",
        "_cmd_doc_decks": "Показать деки",
        "_cmd_doc_deletedeck": "<id> - Удалить деку",
        "_cmd_doc_listdeck": "<id> - Показать деку",
        "_cmd_doc_editdeck": "<id> - Редактировать деку",
        "_cmd_doc_savedeck": "<reply> - Сохранить деку",
        "_cmd_doc_htmldeck": "<id> - Сгенерировать оффлайн-тестирование по деке",
        "_cls_doc": "Флеш-карты для обучения",
    }

    async def client_ready(self, client, db):
        self.decks = self.get("decks", {})

    def get_fucking_deck_from_fucking_reply(self, fucking_reply, fucking_limit=None):
        if fucking_reply is None:
            return False

        if "#Deck" in fucking_reply.text:
            bitches = 1

            for asshole_fucking_line in fucking_reply.text.split("\n"):
                asshole_fucking_line = asshole_fucking_line.split()
                if len(asshole_fucking_line) > 1:
                    what_the_fuck_am_i_doing_in_3_am_utc = (
                        asshole_fucking_line[1]
                        .replace("<code>", "")
                        .replace("</code>", "")
                        .replace("#", "")
                    )
                    try:
                        int(what_the_fuck_am_i_doing_in_3_am_utc)
                    except Exception:
                        pass

                    if what_the_fuck_am_i_doing_in_3_am_utc in self.decks:
                        if (
                            fucking_limit is None
                            or not fucking_limit
                            and "#Decks" not in fucking_reply.text
                            or bitches == fucking_limit
                        ):
                            return what_the_fuck_am_i_doing_in_3_am_utc
                        else:
                            bitches += 1

        return False

    async def get_from_fucking_message(self, message: Message):
        args = utils.get_args_raw(message)
        try:
            args = args.split()[0]
        except Exception:
            pass

        if args.startswith("#"):
            args = args[1:]

        try:
            int_args = int(args)
        except Exception:
            args = False
            int_args = False

        if int(int_args) < 1000:
            args = self.get_fucking_deck_from_fucking_reply(
                await message.get_reply_message(), int_args
            )

        if not args or args not in self.decks:
            await utils.answer(message, self.strings("deck_not_found"))
            await asyncio.sleep(2)
            await message.delete()
            return False

        return args

    async def newdeckcmd(self, message: Message):
        """<name> - New deck of cards"""

        args = utils.get_args_raw(message)
        if args == "":
            await utils.answer(message, self.strings("no_deck_name"))
            await asyncio.sleep(2)
            await message.delete()
            return

        random_id = str(randint(10000, 99999))

        self.decks[random_id] = {"name": args, "cards": [("sample", "sample")]}

        self.set("decks", self.decks)
        await utils.answer(
            message,
            self.strings("deck_created").format(random_id, args),
        )

    async def deckscmd(self, message: Message):
        """List decks"""
        res = "<b>#Decks:</b>\n\n"
        for counter, (item_id, item) in enumerate(self.decks.items(), start=1):
            if len(item["cards"]) == 0:
                items = "No cards"
            else:
                items = "".join(
                    f"\n   {front} - {back}" for front, back in item["cards"][:2]
                )
                if len(item["cards"]) > 2:
                    items += "\n   <...>"
            res += f"🔸<b>{counter}.</b> <code>{item_id}</code> | {item['name']}<code>{items}</code>\n\n"
        await utils.answer(message, res)

    async def deletedeckcmd(self, message: Message):
        """<id> - Delete deck"""
        deck_id = await self.get_from_fucking_message(message)
        if not deck_id:
            return

        del self.decks[deck_id]
        self.set("decks", self.decks)
        reply = await message.get_reply_message()
        if reply:
            if "#Decks" in reply.text:
                await self.deckscmd(reply)
            elif "#Deck" in reply.text:
                await reply.edit(reply.text + "\n" + self.strings("deck_removed"))
        await utils.answer(message, self.strings("deck_removed"))

    async def listdeckcmd(self, message: Message):
        """<id> - List deck items"""
        deck_id = await self.get_from_fucking_message(message)
        if not deck_id:
            return

        deck = self.decks[deck_id]
        res = f"📋#Deck #{deck_id} <b>{deck['name']}</b>:\n➖➖➖➖➖➖➖➖➖➖"
        for i, (front, back) in enumerate(deck["cards"], start=1):
            res += f"\n<b>{i}. {front} - {back}</b>"
        await utils.answer(message, res)

    async def editdeckcmd(self, message: Message):
        """<id> - Edit deck items"""
        deck_id = await self.get_from_fucking_message(message)
        if not deck_id:
            return

        deck = self.decks[deck_id]
        res = f"📋#Deck #{deck_id} \"<b>{deck['name']}</b>\":\n➖➖➖➖➖➖➖➖➖➖"
        for front, back in deck["cards"]:
            res += f"\n<b>{front} - {back}</b>"

        res += "\n➖➖➖➖➖➖➖➖➖➖\nEdit and type <code>.savedeck</code> in reply to this message\n<i>Note: you can edit title and cards, but other message should stay untouched, otherwise it can be saved incorrectly!</i> #Editing"

        await utils.answer(message, res)

    def remove_html(self, text):
        return re.sub(r"<.*?>", "", text)

    async def savedeckcmd(self, message: Message):
        """<reply> - Save deck. Do not use if you don't know what is this"""
        reply = await message.get_reply_message()
        if not reply or "#Editing" not in reply.text:
            await utils.answer(message, self.strings("save_deck_no_reply"))
            await asyncio.sleep(2)
            await message.delete()
            return False

        deck_id = await self.get_from_fucking_message(message)
        if not deck_id:
            return

        deck = self.decks[deck_id]
        self.decks[deck_id]["cards"] = []
        items = reply.text.split("\n")
        for item in items[2:-3]:
            self.decks[deck_id]["cards"].append(
                (
                    self.remove_html(item.split(" - ")[0]),
                    self.remove_html(item.split(" - ")[1]),
                )
            )

        try:
            self.decks[deck_id]["name"] = self.remove_html(
                re.search(r"&quot;(.+?)&quot;", items[0]).group(1)
            )
        except Exception:
            pass

        self.set("decks", self.decks)

        res = f"📋#Deck #{deck_id} <b>{deck['name']}</b>:\n➖➖➖➖➖➖➖➖➖➖"
        for i, (front, back) in enumerate(deck["cards"], start=1):
            res += f"\n<b>{i}. {front} - {back}</b>"
        res += "\n➖➖➖➖➖➖➖➖➖➖\n" + self.strings("deck_saved")

        await utils.answer(reply, res)
        await message.delete()

    async def htmldeckcmd(self, message: Message):
        """<id> - Generates the page with specified deck"""
        deck_id = await self.get_from_fucking_message(message)
        if not deck_id:
            return

        deck = self.decks[deck_id]
        await utils.answer(message, self.strings("generating_page"))
        deck_name = deck["name"]
        loc_cards = deck["cards"].copy()
        cards = dict(loc_cards)
        json_cards = json.dumps(cards).replace('"', '\\"')
        txt = io.BytesIO(
            TEMPLATE.replace("^title_deck_name^", deck_name)
            .replace("^deck_name^", deck_name)
            .replace("^json_cards^", json_cards)
            .encode("utf-8")
        )
        txt.name = "testing.html"
        await message.delete()
        await message.client.send_file(
            message.to_id,
            txt,
            caption=self.strings("offline_testing").format(deck_name),
        )
