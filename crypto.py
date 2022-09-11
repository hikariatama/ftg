#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://img.icons8.com/3d-plastilina/344/3d-plastilina-three-quarter-view-of-a-bitcoin-emblem.png
# meta developer: @hikarimods
# meta banner: https://mods.hikariatama.ru/badges/crypto.jpg

import asyncio
import difflib
import re
import logging
import requests

from lxml import etree

from telethon.tl.types import Message
from telethon.errors.rpcerrorlist import BotResponseTimeoutError

from .. import loader, utils
from ..inline.types import InlineCall

logger = logging.getLogger(__name__)

AMOUNT_REGEX = (
    r"(?:Сheck for |Чек на)(.*?\(.*?\))(?:\.| given to| для| with description.| с"
    r" описанием.)"
)
INVOICE_AMOUNT_REGEX = (
    r"(?:Invoice for |Счёт на)(.*?)(?:\.$| with description.| с описанием.)"
)
RECEIVER_REGEX = r"(?:given to | для )(.*?)(?:\.| with| с описанием)"
BALANCE_REGEX = r"(?:Available: |Доступно: )(.*)"

EMOJI_MAP = {
    "USDT": "<emoji document_id=6032709766881479783>💵</emoji>",
    "TON": "<emoji document_id=6032804204622384196>💵</emoji>",
    "BTC": "<emoji document_id=6032744483102133873>💵</emoji>",
    "ETH": "<emoji document_id=6032967271645711263>💵</emoji>",
    "BNB": "<emoji document_id=6032733926072520137>💵</emoji>",
    "BUSD": "<emoji document_id=6033097439219551284>💵</emoji>",
    "USDC": "<emoji document_id=6030553792083135328>💵</emoji>",
}

RATES_CONFIG = {
    "USD": "<emoji document_id=6323374027985389586>🇺🇸</emoji> <b>USD: {} $</b>",
    "RUB": "<emoji document_id=6323139226418284334>🇷🇺</emoji> <b>RUB: {} ₽</b>",
    "EUR": "<emoji document_id=6323217102765295143>🇪🇺</emoji> <b>EUR: {} €</b>",
    "UAH": "<emoji document_id=6323289850921354919>🇺🇦</emoji> <b>UAH: {} ₴</b>",
    "KZT": "<emoji document_id=6323135275048371614>🇰🇿</emoji> <b>KZT: {} ₸</b>",
    "PLN": "<emoji document_id=6323602387101550101>🇵🇱</emoji> <b>PLN: {} zł</b>",
    "UZS": "<emoji document_id=6323430017179059570>🇺🇿</emoji> <b>UZS: {} сўм</b>",
    "INR": "<emoji document_id=6323181871148566277>🇮🇳</emoji> <b>INR: {} ₹</b>",
    "TRY": "<emoji document_id=6321003171678259486>🇹🇷</emoji> <b>TRY: {} ₺</b>",
}


@loader.tds
class Crypto(loader.Module):
    """Some basic stuff with cryptocurrencies and @CryptoBot"""

    strings = {
        "name": "Crypto",
        "no_args": (
            "<emoji document_id=6053166094816905153>💀</emoji> <b>You need to specify"
            " args</b>"
        ),
        "incorrect_args": (
            "<emoji document_id=6053166094816905153>💀</emoji> <b>Incorrect args</b>"
        ),
        "insufficient_funds": (
            "<emoji document_id=5472363448404809929>👛</emoji> <b>Insufficient funds</b>"
        ),
        "empty_balance": (
            "<emoji document_id=5370646412243510708>😭</emoji> <b>You don't have any"
            " money</b>"
        ),
        "confirm_check": (
            "👛 <b>Please, confirm that info below is valid:</b>\n\n<b>🪙 Amount:"
            " {amount}</b>{receiver}{comment}\n\n{balance}"
        ),
        "confirm_invoice": (
            "👛 <b>Please, confirm that info below is valid:</b>\n\n<b>🪙 Amount:"
            " {amount}</b>{comment}\n\n{balance}"
        ),
        "check": (
            "{emoji} <b>Check for {amount}</b>{receiver}{comment}\n\n<emoji"
            ' document_id=5188509837201252052>💸</emoji> <b><a href="{link}">Receive'
            " funds</a></b>"
        ),
        "invoice": (
            "{emoji} <b>Invoice for {amount}</b>{comment}\n\n<emoji"
            ' document_id=5188509837201252052>💸</emoji> <b><a href="{link}">Proceed'
            " with payment</a></b>"
        ),
        "comment": "\n💬 <b>Comment: </b><i>{}</i>",
        "receiver": "\n👤 <b>Receiver: </b><i>{}</i>",
        "available": "💰 <b>Available: </b><i>{}</i>",
        "send_check": "👛 Send check",
        "send_invoice": "👛 Send invoice",
        "cancel": "🔻 Cancel",
        "wallet": (
            "<emoji document_id=5472363448404809929>👛</emoji> <b>Your <a"
            ' href="{}">CryptoBot</a> wallet:</b>\n\n{}'
        ),
        "multi-use_invoice": (
            "<emoji document_id=5472363448404809929>👛</emoji> <b><a"
            ' href="{url}">Multi-use invoice</a></b>'
        ),
        "exchange_rates": "{emoji} <b>{amount} {name} exchange rates:</b>\n\n{rates}",
        "processing_rates": (
            "<emoji document_id=5213452215527677338>⏳</emoji> <b>Stealing some crypto"
            " from exchange...</b>"
        ),
    }

    strings_ru = {
        "no_args": (
            "<emoji document_id=6053166094816905153>💀</emoji> <b>Ты должен указать"
            " аргументы</b>"
        ),
        "incorrect_args": (
            "<emoji document_id=6053166094816905153>💀</emoji> <b>Неверные аргументы</b>"
        ),
        "insufficient_funds": (
            "<emoji document_id=5472363448404809929>👛</emoji> <b>Недостаточно"
            " средств</b>"
        ),
        "confirm_check": (
            "👛 <b>Пожалуйста, подтвердите, что информация ниже верна:</b>\n\n<b>🪙"
            " Сумма: {amount}</b>{receiver}{comment}\n\n{balance}"
        ),
        "confirm_invoice": (
            "👛 <b>Пожалуйста, подтвердите, что информация ниже верна:</b>\n\n<b>🪙"
            " Сумма: {amount}</b>{comment}\n\n{balance}"
        ),
        "check": (
            "{emoji} <b>Чек на {amount}</b>{receiver}{comment}\n\n<emoji"
            ' document_id=5188509837201252052>💸</emoji> <b><a href="{link}">Получить'
            " средства</a></b>"
        ),
        "invoice": (
            "{emoji} <b>Счёт на {amount}</b>{comment}\n\n<emoji"
            ' document_id=5188509837201252052>💸</emoji> <b><a href="{link}">Оплатить'
            "</a></b>"
        ),
        "comment": "\n💬 <b>Комментарий: </b><i>{}</i>",
        "receiver": "\n👤 <b>Получатель: </b><i>{}</i>",
        "available": "💰 <b>Доступно: </b><i>{}</i>",
        "send_check": "👛 Отправить чек",
        "send_invoice": "👛 Отправить счёт",
        "cancel": "🔻 Отмена",
        "wallet": (
            "<emoji document_id=5472363448404809929>👛</emoji> <b>Твой <a"
            ' href="{}">CryptoBot</a> кошелек:</b>\n\n{}'
        ),
        "multi-use_invoice": (
            "<emoji document_id=5472363448404809929>👛</emoji> <b><a"
            ' href="{url}">Многоразовый счёт</a></b>'
        ),
        "processing_rates": (
            "<emoji document_id=5213452215527677338>⏳</emoji> <b>Краду криптовалюту с"
            " биржи...</b>"
        ),
        "exchange_rates": "{emoji} <b>Курс {amount} {name}:</b>\n\n{rates}",
        "empty_balance": (
            "<emoji document_id=5370646412243510708>😭</emoji> <b>На балансе ни"
            " гроша</b>"
        ),
    }

    def __init__(self):
        self.bot = "@CryptoBot"
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "spoiler_balance",
                True,
                "Hide balance under spoiler",
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "hide_balance",
                False,
                "Do not show balance at all",
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "valutes",
                list(RATES_CONFIG),
                "Valutes to show in exchange rates",
                validator=loader.validators.Series(
                    loader.validators.Choice(list(RATES_CONFIG))
                ),
            ),
            loader.ConfigValue(
                "use_testnet",
                False,
                "Use testnet version of CryptoBot",
                validator=loader.validators.Boolean(),
                on_change=lambda: asyncio.ensure_future(self._process_config()),
            ),
        )

    async def _process_config(self):
        await asyncio.sleep(0.5)
        self.bot = "@CryptoBot" if not self.config["debug"] else "@CryptoTestnetBot"

    async def _form_action(
        self,
        call: InlineCall,
        args: str,
        message: Message,
        formatting: dict,
        name: str,
        index: int,
    ):
        query = await self._client.inline_query(self.bot, args)
        result = await query[index].click("me")
        await result.delete()
        await self._client.send_message(
            message.peer_id,
            self.strings(name).format(
                **formatting,
                link=result.reply_markup.rows[0].buttons[0].url,
                emoji=next(
                    (
                        emoji
                        for trigger, emoji in EMOJI_MAP.items()
                        if trigger in query[0].description
                    ),
                    "<emoji document_id=5471952986970267163>💎</emoji>",
                ),
            ),
            reply_to=message.reply_to_msg_id,
            link_preview=False,
        )
        await call.delete()

    @loader.command(ru_doc="<сумма> [человек] [комментарий] - Выписать чек")
    async def check(self, message: Message):
        """<amount> [person] [comment] - Send check"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings("no_args"))
            return

        if args.split()[0] == "0":
            receiver = (
                args.split()[1]
                if len(args.split()) > 1 and args.split()[1].startswith("@")
                else ""
            )
            if receiver:
                receiver = self.strings("receiver").format(receiver)

            comment = (
                (
                    args.split(maxsplit=2)[2]
                    if len(args.split()) > 2 and args.split()[1].startswith("@")
                    else args.split(maxsplit=1)[1]
                )
                if len(args.split()) > 1
                else ""
            )

            if comment:
                comment = self.strings("comment").format(comment)

            await utils.answer(
                message,
                self.strings("check").format(
                    amount="1.205487 BTC (25621.80$)",
                    comment=comment,
                    receiver=receiver,
                    link="https://www.youtube.com/watch?v=hGA6MGBuaCs",
                    emoji=EMOJI_MAP["BTC"],
                ),
            )
            return

        try:
            query = await asyncio.wait_for(
                self._client.inline_query(self.bot, args),
                timeout=3000,
            )
        except (BotResponseTimeoutError, asyncio.TimeoutError):
            await utils.answer(message, self.strings("incorrect_args"))
            return

        article = query[0].description.strip()
        if not article.startswith("Сheck") and not article.startswith("Чек"):
            await utils.answer(message, self.strings("insufficient_funds"))
            return

        amount = re.search(AMOUNT_REGEX, article)[1]
        if re.search(RECEIVER_REGEX, article):
            receiver = self.strings("receiver").format(
                utils.escape_html(re.search(RECEIVER_REGEX, article)[1])
            )
        else:
            receiver = ""

        if re.search(BALANCE_REGEX, article) and not self.config["hide_balance"]:
            balance = self.strings("available").format(
                (
                    "<tg-spoiler>{}</tg-spoiler>"
                    if self.config["spoiler_balance"]
                    else "{}"
                ).format(utils.escape_html(re.search(BALANCE_REGEX, article)[1]))
            )
        else:
            balance = ""

        comment = args.split(maxsplit=1)[1] if len(args.split()) > 1 else ""
        if receiver:
            comment = comment.split(maxsplit=1)[1] if len(comment.split()) > 1 else ""

        if comment:
            comment = self.strings("comment").format(utils.escape_html(comment))

        await self.inline.form(
            message=message,
            text=self.strings("confirm_check").format(
                amount=amount,
                comment=comment,
                receiver=receiver,
                balance=balance,
            ),
            reply_markup=[
                {
                    "text": self.strings("send_check"),
                    "callback": self._form_action,
                    "args": (
                        args,
                        message,
                        {"amount": amount, "comment": comment, "receiver": receiver},
                        "check",
                        0,
                    ),
                },
                {"text": self.strings("cancel"), "action": "close"},
            ],
        )

    @loader.command(ru_doc="Показать баланс криптокошелька")
    async def wallet(self, message: Message):
        """Show wallet balance"""
        async with self._client.conversation(self.bot) as conv:
            m = await conv.send_message("/wallet")
            r = await conv.get_response()

            await m.delete()
            buttons = utils.array_sum([row.buttons for row in r.reply_markup.rows])
            button = next(
                (btn for btn in buttons if btn.text == "Show Small Balances"), None
            )
            if button:
                await r.click(data=button.data)
                r = (await self._client.get_messages(r.peer_id, ids=[r.id]))[0]

            await r.delete()

        info = "\n\n".join(
            f"{next((emoji for trigger, emoji in EMOJI_MAP.items() if trigger in line), '<emoji document_id=5471952986970267163>💎</emoji>')} <b>{line.split(maxsplit=1)[1]}</b>"
            for line in r.raw_text.splitlines()
            if line.startswith("·") and ": 0 " not in line
        )

        await utils.answer(
            message,
            self.strings("wallet").format(f"https://t.me/{self.bot.strip('@')}", info)
            if info
            else self.strings("empty_balance"),
        )

    @loader.command(ru_doc="[-o - не создавать новый] - Отправить мультисчёт")
    async def muinvoice(self, message: Message):
        """[-o - don't create new one] Send multi-use invoice"""
        if "-o" in utils.get_args_raw(message) and self.get("muinvoice_url"):
            url = self.get("muinvoice_url")
        else:
            query = await self._client.inline_query(self.bot, "")
            m = await query[0].click("me")
            await m.delete()
            url = m.reply_markup.rows[0].buttons[0].url
            self.set("muinvoice_url", url)

        await utils.answer(
            message,
            self.strings("multi-use_invoice").format(url=url),
        )

    @loader.command(ru_doc="<сумма> [комментарий] - Выставить счет")
    async def invoice(self, message: Message):
        """<amount> [comment] - Send invoice"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings("no_args"))
            return

        try:
            query = await asyncio.wait_for(
                self._client.inline_query(self.bot, args),
                timeout=3000,
            )
        except (BotResponseTimeoutError, asyncio.TimeoutError):
            await utils.answer(message, self.strings("incorrect_args"))
            return

        article = query[-1].description.strip()
        if not article.startswith("Invoice") and not article.startswith("Счёт"):
            await utils.answer(message, self.strings("insufficient_funds"))
            return

        amount = re.search(INVOICE_AMOUNT_REGEX, article)[1]

        if re.search(BALANCE_REGEX, article) and not self.config["hide_balance"]:
            balance = self.strings("available").format(
                (
                    "<tg-spoiler>{}</tg-spoiler>"
                    if self.config["spoiler_balance"]
                    else "{}"
                ).format(utils.escape_html(re.search(BALANCE_REGEX, article)[1]))
            )
        else:
            balance = ""

        comment = args.split(maxsplit=1)[1] if len(args.split()) > 1 else ""
        if comment:
            comment = self.strings("comment").format(utils.escape_html(comment))

        await self.inline.form(
            message=message,
            text=self.strings("confirm_invoice").format(
                amount=amount,
                comment=comment,
                balance=balance,
            ),
            reply_markup=[
                {
                    "text": self.strings("send_invoice"),
                    "callback": self._form_action,
                    "args": (
                        args,
                        message,
                        {"amount": amount, "comment": comment},
                        "invoice",
                        -1,
                    ),
                },
                {"text": self.strings("cancel"), "action": "close"},
            ],
        )

    @loader.command(ru_doc="[amount] <name> - Показать курс криптовалюты")
    async def rates(self, message: Message):
        """[amount] <name> - Show cryptocurrency exchange rates"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings("no_args"))
            return

        if len(args.split()) > 1 and args[0].isdigit():
            amount = float(args.split(maxsplit=1)[0])
            args = args.split(maxsplit=1)[1]
        else:
            amount = 1

        message = await utils.answer(message, self.strings("processing_rates"))

        valutes = {
            valute.getchildren()[1].text: float(
                valute.getchildren()[4].text.replace(",", ".")
            )
            / int(valute.getchildren()[2].text)
            for valute in etree.fromstring(
                (
                    await utils.run_sync(
                        requests.get, "https://www.cbr.ru/scripts/XML_daily.asp"
                    )
                ).content
            ).getchildren()
        }

        def to_RUB(price_usd: float) -> float:
            return price_usd * valutes["USD"]

        def to_XXX(price_usd: float, name: str) -> float:
            return to_RUB(price_usd) / valutes[name]

        crypto = {
            crypto["symbol"]: {
                "rates": {
                    "USD": float(crypto["priceUsd"]),
                    "RUB": to_RUB(float(crypto["priceUsd"])),
                    **{
                        name: to_XXX(float(crypto["priceUsd"]), name)
                        for name in self.config["valutes"]
                        if name not in {"USD", "RUB"}
                    },
                },
                "name": crypto["name"],
            }
            for crypto in (
                await utils.run_sync(requests.get, "https://api.coincap.io/v2/assets")
            ).json()["data"]
        }

        closest_crypto = difflib.get_close_matches(
            args.upper(),
            crypto.keys(),
            n=1,
        )
        if not closest_crypto:
            await utils.answer(message, self.strings("incorrect_args"))
            return

        exchange_rates = crypto[closest_crypto[0]]["rates"]
        await utils.answer(
            message,
            self.strings("exchange_rates").format(
                emoji=next(
                    (
                        emoji
                        for name, emoji in EMOJI_MAP.items()
                        if name in closest_crypto[0] or closest_crypto[0] in name
                    ),
                    "<emoji document_id=5471952986970267163>💎</emoji>",
                ),
                name=crypto[closest_crypto[0]]["name"],
                rates="\n".join(
                    RATES_CONFIG[valute].format(
                        f"{exchange_rates[valute] * amount:_.2f}".replace("_", " ")
                    )
                    for valute in self.config["valutes"]
                ),
                amount=amount,
            ),
        )
