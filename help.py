"""
    Copyright 2021 t.me/innocoffee
    Licensed under the Apache License, Version 2.0
    
    Author is not responsible for any consequencies caused by using this
    software or any of its parts. If you have any questions or wishes, feel
    free to contact Dan by sending pm to @innocoffee_alt.
"""

#<3 title: Help
#<3 pic: https://img.icons8.com/fluency/48/000000/chatbot.png
#<3 desc: Милая и красивая помощь с Японией, лисичками, а также уровнями доступа к командам.


import inspect
from .. import loader, utils, main, security


@loader.tds
class HelpMod(loader.Module):
    """Provides this help message"""
    strings = {"name": "Help",
               "bad_module": '<b>🦊 I don\'t know what</b> "<code>{}</code>" <b>is!</b>',
               "single_mod_header": "<b>🦊 Info about</b> <u>{}</u>:\n",
               "single_cmd": "\n🧊 {}\n",
               "undoc_cmd": "🦊 No docs",
               "all_header": '🦊 <b>{} mods available:</b>\n',
               "mod_tmpl": '\n🇯🇵 <code>{}</code>',
               "first_cmd_tmpl": ": ( {}",
               "cmd_tmpl": " | {}"}

    @loader.unrestricted
    async def helpcmd(self, message):
        """.help [module] [-fl] [-f - ignore security checks] [-l level - set security level to parse]"""
        args = utils.get_args_raw(message)
        force = False
        print(args)
        if '-f' in args:
            args = args.replace(' -f', '').replace('-f', '')
            force = True
        level = False
        if '-l' in args:
            try:
                level = int(re.search(r'[ ]?-l ([0-9]+)', args).group(1))
            except:
                pass

            args = re.sub(r' -l ([0-9]+)', '', args)

        id = message.sender_id
        if args:
            module = None
            for mod in self.allmodules.modules:
                if mod.strings("name", message).lower() == args.lower():
                    module = mod
            if module is None:
                await utils.answer(message, self.strings("bad_module", message).format(args))
                return
            # Translate the format specification and the module separately
            try:
                name = module.strings("name", message)
            except KeyError:
                name = getattr(module, "name", "ERROR")
            reply = self.strings("single_mod_header", message).format(utils.escape_html(name),
                                                                      utils.escape_html((self.db.get(main.__name__,
                                                                                                     "command_prefix",
                                                                                                     False) or ".")[0]))
            if module.__doc__:
                reply += "\n" + \
                    "\n".join(
                        "  " + t for t in utils.escape_html(inspect.getdoc(module)).split("\n"))
            commands = {name: func for name, func in module.commands.items()
                        if await self.allmodules.check_security(message, func)}
            for name, fun in commands.items():
                reply += self.strings("single_cmd", message).format(name)
                if fun.__doc__:
                    reply += utils.escape_html("\n".join("    " +
                                                         t for t in inspect.getdoc(fun).split("\n")))
                else:
                    reply += self.strings("undoc_cmd", message)
        else:
            count = 0
            for i in self.allmodules.modules:
                try:
                    if len(i.commands) != 0:
                        count += 1
                except:
                    pass
            reply = self.strings("all_header", message).format(count)
            shown_warn = False
            for mod in self.allmodules.modules:
                if len(mod.commands) != 0:
                    try:
                        name = mod.strings("name", message)
                    except KeyError:
                        name = getattr(mod, "name", "ERROR")
                    reply += self.strings("mod_tmpl", message).format(name)
                    first = True
                    commands = [name for name, func in mod.commands.items()
                                if await self.allmodules.check_security(message, func) or force]
                    for cmd in commands:
                        if first:
                            reply += self.strings("first_cmd_tmpl",
                                                  message).format(cmd)
                            first = False
                        else:
                            reply += self.strings("cmd_tmpl",
                                                  message).format(cmd)
                    if len(commands) == 0:
                        if not shown_warn:
                            reply = '<i>Показаны только те модули, для которых вам хватает разрешений для выполнения</i>\n' + reply
                            shown_warn = True
                        reply = '\n'.join(reply.split('\n')[:-1])
                    else:
                        reply += " )"

        await utils.answer(message, reply)

    async def client_ready(self, client, db):
        self.client = client
        self.is_bot = await client.is_bot()
        self.db = db
