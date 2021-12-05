"""
    Copyright 2021 t.me/innocoffee
    Licensed under the Apache License, Version 2.0
    
    Author is not responsible for any consequencies caused by using this
    software or any of its parts. If you have any questions or wishes, feel
    free to contact Dan by sending pm to @innocoffee_alt.
"""

#<3 title: Img2Pdf
#<3 pic: https://img.icons8.com/fluency/48/000000/sync-settings.png
#<3 desc: Упаковать картинки в единый pdf

from .. import loader, utils
from PIL import Image, UnidentifiedImageError
import io
import tempfile
import logging

logger = logging.getLogger(__name__)

@loader.tds
class Img2PdfMod(loader.Module):
    """Packs images to pdf"""
    strings = {
        "name":"Img2Pdf"
    }

    async def client_ready(self, client, db):
        self.db = db
        self.client = client

    @loader.unrestricted
    async def img2pdfcmd(self, message):
        """<filename | optional> - Pack images into pdf"""
        try:
            start_offset = message.id if message.media else (await message.get_reply_message()).id
        except:
            return await utils.answer(message, self.strings('no_file'))

        images = []

        async for ms in self.client.iter_messages(message.peer_id, offset_id=start_offset - 1, reverse=True):
            if not ms.media: break
            im = await self.client.download_file(ms.media)
            try:
                images.append(Image.open(io.BytesIO(im)))
            except UnidentifiedImageError: break

        first_image, images = images[0], images[1:]
        file = io.BytesIO()
        first_image.save(file, "PDF", resolution=100.0, save_all=True, append_images=images)
        f = io.BytesIO(file.getvalue())
        f.name = utils.get_args_raw(message) or 'packed_images.pdf'
        await self.client.send_file(message.peer_id, f)
        await message.delete()



