"""
    Copyright 2021 t.me/innocoffee
    Licensed under the Apache License, Version 2.0
    
    Author is not responsible for any consequencies caused by using this
    software or any of its parts. If you have any questions or wishes, feel
    free to contact Dan by sending pm to @innocoffee_alt.
"""

#<3 title: LastCommand
#<3 pic: https://img.icons8.com/fluency/48/000000/last-12-hours.png
#<3 desc: Выполнить предыдущую команду

from .. import loader, utils
import asyncio
import os

@loader.tds
class LastCommandMod(loader.Module):
    """Execute last command"""
    strings = {'name': 'LastCommand',
    'modified': '<b>Successfully modified dispatcher.py and main.py. Restarting userbot</b>',
    'uninstalled': '<b>Successfully modified dispatcher.py and main.py. Uninstalling mod and restarting userbot</b>', 
    'no_command': '<b>No command to execute</b>',
    'already_installed': '<b>Module is already installed. No changes occured</b>'}

    async def client_ready(self, client, db):
        self.lc = False
        self.msg = False
        self.client = client

    async def install_lccmd(self, message):
        """.install_lc - Should be performed only once. EDITS dispatcher.py AND main.py, BE CAREFUL!"""
        edited = False
        disp = open('friendly-telegram/dispatcher.py', 'r').read()
        if 'modded by @innocoffee\'s mod' not in disp:
            edited = True
            disp = disp.replace("""
\t\t\ttry:
\t\t\t\tawait func(message)
\t\t\texcept Exception as e:
\t\t\t\tlogging.exception("Command failed")""", """
\t\t\ttry:
\t\t\t\tif '.lc' not in message.text:
\t\t\t\t\tself.last_command = func
\t\t\t\t\tself.last_command_msg = message
\t\t\t\tawait func(message)
\t\t\texcept Exception as e:
\t\t\t\tlogging.exception("Command failed")""")

            disp = '#modded by @innocoffee\'s mod\n\n' + disp
            open('friendly-telegram/dispatcher.py', 'w').write(disp)


        main = open('friendly-telegram/main.py', 'r').read()
        if 'modded by @innocoffee\'s mod' not in main:
            edited = True
            main = main.replace("""dispatcher = CommandDispatcher(modules, db, is_bot, __debug__ and arguments.self_test, no_nickname)""", """dispatcher = CommandDispatcher(modules, db, is_bot, __debug__ and arguments.self_test, no_nickname)\n\t\t\tloader.dispatcher = dispatcher""")

            main = '#modded by @innocoffee\'s mod\n\n' + main
            open('friendly-telegram/main.py', 'w').write(main)
        if edited:
            await utils.answer(message, self.strings('modified', message))
            await self.allmodules.commands['restart'](await self.client.send_message('me', 'restarting'))
        else:
            await utils.answer(message, self.strings('already_installed', message))
            await asyncio.sleep(3)
            await message.delete()
            return

    async def lccmd(self, message):
        if loader.dispatcher.last_command is not None and loader.dispatcher.last_command_msg is not None:
            message.text = loader.dispatcher.last_command_msg.text
            await loader.dispatcher.last_command(message)
        else:
            await utils.answer(message, self.strings('no_command', message))
            await asyncio.sleep(3)
            await message.delete()
            return

    async def uninstall_lccmd(self, message):
        """.uninstall_lc - Should be performed only once. EDITS dispatcher.py AND main.py, BE CAREFUL!"""
        disp = open('friendly-telegram/dispatcher.py', 'r').read()
        if 'modded by @innocoffee\'s mod' not in disp:
            disp = disp.replace("""
\t\t\ttry:
\t\t\t\tif '.lc' not in message.text:
\t\t\t\t\tself.last_command = func
\t\t\t\t\tself.last_command_msg = message
\t\t\t\tawait func(message)
\t\t\texcept Exception as e:
\t\t\t\tlogging.exception("Command failed")""", """
\t\t\ttry:
\t\t\t\tawait func(message)
\t\t\texcept Exception as e:
\t\t\t\tlogging.exception("Command failed")""")

            disp = disp.replace('#modded by @innocoffee\'s mod\n\n', '')
            open('friendly-telegram/dispatcher.py', 'w').write(disp)


        main = open('friendly-telegram/main.py', 'r').read()
        if 'modded by @innocoffee\'s mod' not in main:
            main = main.replace("""dispatcher = CommandDispatcher(modules, db, is_bot, __debug__ and arguments.self_test, no_nickname)\n\t\t\tloader.dispatcher = dispatcher""", """dispatcher = CommandDispatcher(modules, db, is_bot, __debug__ and arguments.self_test, no_nickname)""")

            main = main.replace('#modded by @innocoffee\'s mod\n\n', '')
            open('friendly-telegram/main.py', 'w').write(main)
        
        await utils.answer(message, self.strings('uninstalled', message))
        # await self.allmodules.commands['unloadmod'](await self.client.send_message('me', '.unloadmod LastCommand'))
        # await self.allmodules.commands['restart'](await self.client.send_message('me', 'restarting'))
