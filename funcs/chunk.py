import asyncio
from time import time

import httpx
import numpy as np
from PIL import Image, ImageChops, ImageOps


class TemplateSt:
    def __init__(self):
        self.totalChunks = 0
        self.madeChunks = 0
        self.messageSent = True
        self.timeMessage = 0
        self.thispc = 20
        self.virginpixels = 0
    def percentage(self):
        return 100*(self.madeChunks/self.totalChunks)
    def thisPercentage(self):
        self.thispc = self.thispc + 20

async def compareImg(inter, coords, filename, tempName, version):
    template = TemplateSt()
    start_time = time()
    img = Image.open(f"{filename}").convert("RGBA")
    canvas = 0
    width, height = img.size

    me = httpx.get("https://pixelplanet.fun/api/me").json()
    colors = me["canvases"][str(canvas)]["colors"]
    csz = me["canvases"][str(canvas)]["size"]
    ch = csz // 2

    c_start_y = (ch + coords[1]) // 256
    c_start_x = (ch + coords[0]) // 256
    c_end_y = (ch + coords[1] + width) // 256
    c_end_x = (ch + coords[0] + height) // 256

    c_occupied_y = c_end_y - c_start_y + 1
    c_occupied_x = c_end_x - c_start_x + 1


    size = me["canvases"][str(canvas)]["size"]
    match version:
        case 'diff':
            image = Image.new("RGB", (c_occupied_x*256, c_occupied_y*256))
        case 'virgins':
            virgins = Image.new("RGBA", (c_occupied_x*256, c_occupied_y*256))
        case 'protected':
            protected = Image.new("RGBA", (c_occupied_x*256, c_occupied_y*256))

    async def get_chunk(client, x, y, x_value, y_value):
        resp = await client.get(
            f"https://pixelplanet.fun/chunks/0/{x}/{y}.bmp")
        resp = resp.content
        print(len(resp))

        match version:
            case 'diff':
                chunk = np.zeros((256, 256, 3), np.uint8)
                for i, value in enumerate(resp):
                    chunk[i // 256, i % 256] = colors[value] if value < 128 else colors[value - 128]
                chunk_image = Image.fromarray(chunk, mode="RGB")
                image.paste(chunk_image, (256*x_value, 256*y_value))
            case 'virgins':
                virginchunk = np.zeros((256, 256, 4), np.uint8)
                for i, value in enumerate(resp):   
                    virginchunk[i // 256, i % 256] = [0,255,0,255] if value == 0 or value == 1 else [0,0,0,0]
                    template.virginpixels = template.virginpixels + 1 if value == 0 or value == 1 else template.virginpixels
                virgin_image = Image.fromarray(virginchunk, mode="RGBA")
                virgins.paste(virgin_image, (256*x_value, 256*y_value))
            case 'protected':
                protectedchunk = np.zeros((256, 256, 4), np.uint8)
                for i, value in enumerate(resp): 
                    protectedchunk[i // 256, i % 256] = [0,255,255,255] if value > 127 else [0,0,0,0]

                protected_image = Image.fromarray(protectedchunk, mode="RGBA")
                protected.paste(protected_image, (256*x_value, 256*y_value))

        template.madeChunks = template.madeChunks + 1
        if template.percentage() > template.thispc:
            template.thisPercentage()
            await inter.edit_original_message(f'Getting chunks for template {tempName}: {template.madeChunks}/{template.totalChunks} ({round(template.percentage())}%)\n[{"🟥"*(round(template.percentage()/10))}{"🟩"*(10-round(template.percentage()/10))}]')

    async def mainFunc():

        async with httpx.AsyncClient() as client:

            tasks = []
            x_value, y_value = 0, 0
            for y_index in range(c_start_y, c_end_y+1):
                for x_index in range(c_start_x, c_end_x+1):
                    tasks.append(asyncio.ensure_future(get_chunk(client, x_index, y_index, x_value, y_value)))
                    template.totalChunks = template.totalChunks + 1
                    x_value += 1
                y_value += 1
                x_value = 0
            await inter.response.send_message(f"Getting your fresh chunks: 0/{template.totalChunks} (0%)\n[{'🟩'*10}]")
            await asyncio.gather(*tasks)
    await mainFunc()
    await inter.edit_original_message(f"Getting your fresh chunks: {template.totalChunks}/{template.totalChunks} (100%)\n[{'🟥'*10}] \nProcessing your chunks.")
    c_start_x = (ch + coords[0]) // 256
    c_start_y = (ch + coords[1]) // 256
    start_in_d_x = coords[0] + (ch - (c_start_x) * 256)
    start_in_d_y = coords[1] + (ch - (c_start_y) * 256)

    match version:
        case 'diff':
            image = image.crop((start_in_d_x, start_in_d_y, start_in_d_x + width, start_in_d_y + height)).convert("RGBA")
        case 'virgins':
            virgins = virgins.crop((start_in_d_x, start_in_d_y, start_in_d_x + width, start_in_d_y + height)).convert("RGBA")
        case 'protected':
            protected = protected.crop((start_in_d_x, start_in_d_y, start_in_d_x + width, start_in_d_y + height)).convert("RGBA")
    match version:
        case 'diff':
            black = Image.new('1', image.size, 0)
            white = Image.new('1', image.size, 1)
            mask = Image.composite(white, black, img)

            def lut(i):
                return 255 if i > 0 else 0

            with ImageChops.difference(img, image) as error_mask:
                error_mask = error_mask.point(lut).convert('L').point(lut).convert('1')
                error_mask = Image.composite(error_mask, black, mask)

            tot = np.array(mask).sum()
            err = np.array(error_mask).sum()
            image.save('bigchunks.png')
        case 'virgins':
            pass
        case 'protected':
            pass
    img.convert('LA').save("grayed.png")
    new_grayed = Image.open("grayed.png").convert("RGBA")
    match version:
        case 'diff':
            image2 = Image.composite(Image.new('RGBA', image.size, (255, 0, 0)), new_grayed, error_mask).save("difference.png")
            return tot, err, (time() - start_time)
        case 'virgins':
            image3 = Image.composite(Image.new('RGBA', virgins.size, (0, 255, 0)), new_grayed, virgins).save("virgins.png")
            print(f'virginpixels =`{template.virginpixels}')
            return template.virginpixels, (time() - start_time)
        case 'protected':
            image4 = Image.composite(Image.new('RGBA', image.size, (0, 0, 255)), new_grayed, protected).save("protected.png")
