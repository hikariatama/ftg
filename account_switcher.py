"""
    Copyright 2021 t.me/hikariatama
    Licensed under the Apache License, Version 2.0
    
    Author is not responsible for any consequencies caused by using this
    software or any of its parts. If you have any questions or wishes, feel
    free to contact Dan by sending pm to @hikari_alt.
"""

# <3 title: AccountSwitcher
# <3 pic: https://img.icons8.com/fluency/48/000000/change-user-male.png
# <3 desc: Быстро переключайся между аккаунтами - аватарка, ник, био и даже юзернейм

from .. import loader, utils
import telethon
import re
import asyncio

@loader.tds
class AccountSwitcherMod(loader.Module):
    """AccountSwitcher"""
    strings = {
        'name': 'AccountSwitcher',
        'reply_required': '🦊 <b>Reply to service message in db chat named <u>acc-switcher-db</u></b>',
        'account_saved': '🦊 <b>Account saved!</b>'
    }

    async def client_ready(self, client, db):
        self.db = db
        self.client = client
        self.accounts = db.get('AccountSwitcher', 'accounts', {})


    async def _search_db(self):
        async for d in self.client.iter_dialogs():
            if d.title == "acc-switcher-db":
                return d.entity

        return (await self.client(telethon.tl.functions.channels.CreateChannelRequest("acc-switcher-db", "This chat will handle your saved account via AccountSwitcher Module", megagroup=True))).chats[0]


    async def _save_acc(self, photo, fn, ln, bio, un):
        accs_db = await self._search_db()
        info = f'<b>First name</b>: "{fn}"\n<b>Last name</b>: "{ln}"\n<b>Bio</b>: "{bio}"\n<b>Username</b>: "{un}"'
        if photo is not None:
            await self.client.send_file(accs_db, photo, caption=info)
        else:
            await self.client.send_message(accs_db, info)



    async def accsavecmd(self, message):
        """[-n] - Save account for future restoring. -n - To save username, and change it while restoring"""
        args = utils.get_args_raw(message)
        full = await self.client(telethon.tl.functions.users.GetFullUserRequest('me'))
        photo, fn, ln, bio, un = None, None, None, None, None
        acc = await message.client.get_entity('me')
        if full.profile_photo: 
            photo = await message.client.download_profile_photo(acc, bytes)
        fn = getattr(acc, 'first_name', None)
        ln = getattr(acc, 'last_name', None)
        un = getattr(acc, 'username', None) if '-n' in args else 'not_saved_username'
        bio = full.about if getattr(full, 'about', None) is not None else ''
        await self._save_acc(photo, fn, ln, bio, un)
        await utils.answer(message, self.strings('account_saved'))


    async def accrestcmd(self, message):
        """<reply to message in db> - Restore account from backup. Your username could be stolen!"""
        reply = await message.get_reply_message()
        if not reply:
            return await utils.answer(message, self.strings('reply_required'))

        chat = await reply.get_chat()
        # if chat.title != "acc-switcher-db":
        #     return await utils.answer(message, self.strings('reply_required'))

        log = ""

        data = re.sub(r'<.*?>', '', reply.message)
        fn = re.search(r'First name: "([^"]+)"', data).group(1)
        ln = re.search(r'Last name: "([^"]+)"', data).group(1)
        bio = re.search(r'Bio: "([^"]+)"', data).group(1)
        un = re.search(r'Username: "([^"]+)"', data).group(1)

        fn = fn if fn != 'None' else None
        ln = ln if ln != 'None' else None
        bio = bio if bio != 'None' else None
        un = un if un != 'None' else None

        if un != 'not_saved_username':
            try:
                await self.client(telethon.tl.functions.account.UpdateUsernameRequest(un))
            except:
                log += "👉🏻 Error while restoring username\n"
        else:
            log += "👉🏻 Username not restored\n"


        try:
            await self.client(telethon.tl.functions.account.UpdateProfileRequest( 
                fn, 
                ln, 
                bio
            )) 
            log += "👉🏻 First name restored\n" if fn is not None else "👉🏻 First name not restored\n"
            log += "👉🏻 Last name restored\n" if ln is not None else "👉🏻 Last name not restored\n"
            log += "👉🏻 Bio restored\n" if bio is not None else "👉🏻 Bio not restored\n"
        except:
            log += "👉🏻 First name not restored\n👉🏻 Last name not restored\n👉🏻 Bio not restored"

        try:
            if reply.media:
                upload = await self.client.upload_file(await self.client.download_media(reply.media)) 
                await self.client(telethon.tl.functions.photos.UploadProfilePhotoRequest(upload))
                log += "👉🏻 Profile photo restored"
            else:
                log += "👉🏻 Profile photo not restored"
        except:
            log += "👉🏻 Profile photo not restored"

        log = re.sub(r'\n{2,}', r'\n', log)

        await utils.answer(message, log)
