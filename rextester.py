"""
    Copyright 2021 t.me/aiexz
    Licensed under the Apache License, Version 2.0
    
    Author is not responsible for any consequencies caused by using this
    software or any of its parts. If you have any questions or wishes, feel
    free to contact Alex by sending pm to @aiexz.
"""

# <3 title: Rextester
# <3 pic: https://img.icons8.com/fluency/48/000000/system-information.png
# <3 desc: Выполнение кода на многих языках программирования

import logging
import typing
import telethon
import functools

if typing.TYPE_CHECKING:
    import loader
    import utils
else:
    from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class RextesterMod(loader.Module):
    """Code evaluation via @rextester_bot"""

    strings = {
        "name": "Rextester",
    }

    async def client_ready(self, client: telethon.TelegramClient, db):
        def get_commands(mod):
            """Introspect the module to get its commands"""
            # https://stackoverflow.com/a/34452/5509575
            return {method_name[:-3]: getattr(mod, method_name) for method_name in dir(mod)
                    if callable(getattr(mod, method_name)) and method_name[-3:] == "cmd"}

        self.rextester_bot = "@rextester_bot"
        self.db = db
        self.client = client
        async with client.conversation(self.rextester_bot) as conv:
            m = await conv.send_message("/languages")
            res = await conv.get_response()
            await conv.mark_read()
            languages_availiable = res.raw_text.replace('/', '').replace(',', '').split()
            await m.delete()
            await res.delete()

        # languages_availiable = langs.replace("/", "").split()
        languages = {lang: False for lang in languages_availiable}
        languages.update(self.db.get("RextesterMod", "languages", {}))
        self.languages = languages
        commands = get_commands(self)
        for lang, enabled in self.languages.items():
            if enabled:
                commands[f"{lang}rx"] = self.register_eval(lang)
        self.commands = commands

    async def rexeval(self, message: telethon.types.Message, language: str):
        args = utils.escape_html(utils.get_args_raw(message))
        async with self.client.conversation(self.rextester_bot) as conv:
            m = await conv.send_message("/" + language + " " + args)
            res = await conv.get_response()
            await conv.mark_read()
            await utils.answer(message, f"<b>👾 Code</b>\n<pre>{args}</pre>\n<b>🎬 Result:</b>\n<pre>{res.raw_text.replace('Result:', '').strip()}</pre>")
            await m.delete()
            await res.delete()


    def register_eval(self, lang: str):
        func_name = f"{lang}rx"
        func = functools.partial(self.rexeval, language=lang)
        func.__module__ = self.__module__
        func.__name__ = func_name
        func.__self__ = self
        func.__doc__ = f"Evaluates {lang} code"
        setattr(func, self.__module__ + "." + func.__name__, loader.support)
        return func

    @loader.owner
    async def togglerxcmd(self, message: telethon.types.Message):
        """Enables one the languages"""
        args = utils.get_args_raw(message)
        if args in self.languages:
            enabled = self.languages[args] = not self.languages[args]
            func_name = f"{args}rx"
            if enabled:
                func = self.register_eval(args)
                self.commands[func_name] = func
                self.allmodules.commands[func_name] = func
            else:
                del self.commands[func_name]
                del self.allmodules.commands[func_name]
            await utils.answer(message, f"{args} is {'enabled' if enabled else 'disabled'}")
            self.db_saver()
        else:
            await utils.answer(message, f"{args} not found")

    @loader.owner
    async def langsrxcmd(self, message: telethon.types.Message):
        """Lists all available languages"""
        await utils.answer(message, " ".join(self.languages.keys()))

    def db_saver(self):
        self.db.set("RextesterMod", "languages", dict(
            filter(lambda x: x[1], self.languages.items())))
