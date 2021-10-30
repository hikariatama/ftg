"""
    Copyright 2021 t.me/innocoffee
    Licensed under the Apache License, Version 2.0
    
    Author is not responsible for any consequencies caused by using this
    software or any of its parts. If you have any questions or wishes, feel
    free to contact Dan by sending pm to @innocoffee_alt.
"""

#<3 title: FlashCards
#<3 pic: https://img.icons8.com/fluency/48/000000/cards.png
#<3 desc: Поможет быстро запомнить информацию, подготовиться к зачету

from .. import loader, utils
import asyncio
from random import randint
import json
import re
import io

#requires: random json


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
        Загрузка карт...
    </div>
    <div class="testing">
        <h1 class="front"></h1>
        <input class="back" type="text" placeholder="Ответ">
    </div>
    <div class="begin button">Начать тестирование</div>

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
                document.querySelector('.front').innerHTML = "Правильно!";
                document.querySelector('.testing').style.background = '#26681e';
            } else {
                document.querySelector('.testing').style.background = '#611a1a';
                document.querySelector('.front').innerHTML = "Неверно. Правильный ответ: " + el.getAttribute('answer');
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
            this.innerHTML = "Проверить ответ";
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
    strings = {'name': 'FlashCards'}

    async def client_ready(self, client, db):
        self.db = db
        try:
            self.decks = json.loads(self.db.get("FlashCards", "decks"))
        except:
            self.decks = {}


    def get_fucking_deck_from_fucking_reply(self, fucking_reply, fucking_limit=None):
        if fucking_reply == None:
            return False

        bitches = 1

        if "#Deck" in fucking_reply.text:
            for asshole_fucking_line in fucking_reply.text.split('\n'):
                asshole_fucking_line = asshole_fucking_line.split()
                if len(asshole_fucking_line) > 1:
                    what_the_fuck_am_i_doing_in_3_am_utc = asshole_fucking_line[1].replace('<code>', '').replace('</code>', '').replace('#', '')
                    try:
                        int(what_the_fuck_am_i_doing_in_3_am_utc)
                    except:
                        pass

                    if what_the_fuck_am_i_doing_in_3_am_utc in self.decks:
                        if fucking_limit == None or fucking_limit == False and "#Decks" not in fucking_reply.text or bitches == fucking_limit:
                            return what_the_fuck_am_i_doing_in_3_am_utc
                        else:
                            bitches += 1

        return False

    async def get_from_fucking_message(self, message):
        args = utils.get_args_raw(message)
        try:
            args = args.split()[0]
        except:
            pass

        if args.startswith('#'):
            args = args[1:]

        try:
            int_args = int(args)
        except:
            args = False
            int_args = False

        if int(int_args) < 1000:
            args = self.get_fucking_deck_from_fucking_reply(await message.get_reply_message(), int_args)

        if not args or args not in self.decks:
            await utils.answer(message, '<b>🚫 Deck not found</b')
            await asyncio.sleep(2)
            await message.delete()
            return False

        return args


    async def newdeckcmd(self, message):
        """.newdeck <name> - New deck of cards"""

        args = utils.get_args_raw(message)
        if args == "":
            await utils.answer(message, '<b>You haven\'t provided deck name</b>')
            await asyncio.sleep(2)
            await message.delete()
            return

        random_id = str(randint(10000, 99999))

        self.decks[random_id] = {
            'name': args,
            'cards': [('sample', 'sample')]
        }

        self.db.set("FlashCards", "decks", json.dumps(self.decks))
        await utils.answer(message, f"#Deck <code>#{random_id}</code> <b>{args}</b> successfully created!")

    async def deckscmd(self, message):
        """.decks - List decks"""
        res = "<b>#Decks:</b>\n\n"
        counter = 1
        for item_id, item in self.decks.items():
            if len(item['cards']) == 0:
                items = 'No cards'
            else:
                items = ""
                for front, back in item['cards'][:2]:
                    items += f'\n   {front} - {back}'

                if len(item['cards']) > 2:
                    items += "\n   <...>"
            res += f"🔸<b>{counter}.</b> <code>{item_id}</code> | {item['name']}<code>{items}</code>\n\n"
            counter += 1
        await utils.answer(message, res)

    async def deletedeckcmd(self, message):
        """.deletedeck <id> - Delete deck"""
        deck_id = await self.get_from_fucking_message(message)
        if not deck_id:
            return

        del self.decks[deck_id]
        self.db.set("FlashCards", "decks", json.dumps(self.decks))
        reply = await message.get_reply_message()
        if reply and '#Decks' in reply.text:
            await self.deckscmd(reply)
        elif reply and '#Deck' in reply.text:
            await reply.edit(reply.text + '\n<b>🚫 Deck removed</b>')
        await utils.answer(message, '<b>✅ Deck removed</b>')
        await asyncio.sleep(2)
        await message.delete()


    async def listdeckcmd(self, message):
        """.listdeck <id> - List deck items"""
        deck_id = await self.get_from_fucking_message(message)
        if not deck_id:
            return

        deck = self.decks[deck_id]
        res = f"📋#Deck #{deck_id} <b>{deck['name']}</b>:\n➖➖➖➖➖➖➖➖➖➖"
        i = 1
        for front, back in deck['cards']:
            res += f"\n<b>{i}. {front} - {back}</b>"
            i += 1

        await utils.answer(message, res)

    async def editdeckcmd(self, message):
        """.editdeck <id> - Edit deck items"""
        deck_id = await self.get_from_fucking_message(message)
        if not deck_id:
            return

        deck = self.decks[deck_id]
        res = f"📋#Deck #{deck_id} \"<b>{deck['name']}</b>\":\n➖➖➖➖➖➖➖➖➖➖"
        for front, back in deck['cards']:
            res += f"\n<b>{front} - {back}</b>"

        res += "\n➖➖➖➖➖➖➖➖➖➖\nEdit and type <code>.savedeck</code> in reply to this message\n<i>Note: you can edit title and cards, but other message should stay untouched, otherwise it can be saved incorrectly!</i> #Editing"

        await utils.answer(message, res)

    def remove_html(self, text):
        return re.sub(r'<.*?>', '', text)

    async def savedeckcmd(self, message):
        """.savedeck <reply> - Save deck. Do not use if you don't know what is this"""
        reply = await message.get_reply_message()
        if not reply or '#Editing' not in reply.text:
            await utils.answer(message, '<b>🚫 This command should be used in reply to message with deck items.</b')
            await asyncio.sleep(2)
            await message.delete()
            return False

        deck_id = await self.get_from_fucking_message(message)
        if not deck_id:
            return

        deck = self.decks[deck_id]
        self.decks[deck_id]['cards'] = []
        items = reply.text.split('\n')
        for item in items[2:-3]:
            self.decks[deck_id]['cards'].append((self.remove_html(item.split(' - ')[0]), self.remove_html(item.split(' - ')[1])))

        
        try:
            self.decks[deck_id]['name'] = self.remove_html(re.search(r'&quot;(.+?)&quot;', items[0]).group(1))
        except:
            pass

        self.db.set("FlashCards", "decks", json.dumps(self.decks))

        res = f"📋#Deck #{deck_id} <b>{deck['name']}</b>:\n➖➖➖➖➖➖➖➖➖➖"
        i = 1
        for front, back in deck['cards']:
            res += f"\n<b>{i}. {front} - {back}</b>"
            i += 1

        res += "\n➖➖➖➖➖➖➖➖➖➖\n✅ <b>Deck saved!</b>"

        await utils.answer(reply, res)
        await message.delete()

    async def htmldeckcmd(self, message):
        """.htmldeck <id> - Generates the page with specified deck"""
        deck_id = await self.get_from_fucking_message(message)
        if not deck_id:
            return

        deck = self.decks[deck_id]
        await utils.answer(message, '<b>⚙️ Generating page, please wait ...</b>')
        deck_name = deck['name']
        loc_cards = deck['cards'].copy()
        cards = {}
        for front, back in loc_cards:
            cards[front] = back
        json_cards = json.dumps(cards).replace('"', '\\"')
        txt = io.BytesIO(TEMPLATE.replace('^title_deck_name^', deck_name).replace('^deck_name^', deck_name).replace('^json_cards^', json_cards).encode('utf-8'))
        txt.name = "testing.html"
        await message.delete()
        await message.client.send_file(message.to_id, txt, caption=f"<b>📖 Offline testing, based on deck {deck_name}</b>")




