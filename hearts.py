"""
    Copyright 2021 t.me/hikariatama
    Licensed under the Apache License, Version 2.0
    
    Author is not responsible for any consequencies caused by using this
    software or any of its parts. If you have any questions or wishes, feel
    free to contact Dan by sending pm to @hikari_alt.
"""

#<3 title: Hearts
#<3 pic: https://img.icons8.com/fluency/48/000000/filled-like.png
#<3 desc: Гигантские милые анимированные сердечки


from .. import loader, utils
from asyncio import sleep
@loader.tds
class HeartsMod(loader.Module):
	strings = {"name": "Heart's"}
	@loader.owner
	async def heartscmd(self, message):
		message = await utils.answer(message, 'ily <3')
		for _ in range(10):
			for heart in ['🤎', '❤', '🧡', '💛', '💚', '💙', '💜', '🖤', '🤍']:
				await utils.answer(message, heart)
				await sleep(0.4)

