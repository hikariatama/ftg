"""
    Copyright 2021 t.me/innocoffee
    Licensed under the Apache License, Version 2.0
    
    Author is not responsible for any consequencies caused by using this
    software or any of its parts. If you have any questions or wishes, feel
    free to contact Dan by sending pm to @innocoffee_alt.
"""

from .. import loader
from asyncio import sleep
@loader.tds
class HeartsMod(loader.Module):
	strings = {"name": "Heart's"}
	@loader.owner
	async def heartscmd(self, message):
		for _ in range(10):
			for heart in ['❤', '🧡', '💛', '💚', '💙', '💜', '🖤', '🤍', '🤎']:
				await message.edit(heart)
				await sleep(0.3)

