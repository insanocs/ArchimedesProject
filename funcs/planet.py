import asyncio
import time
from io import BytesIO
from pickletools import optimize

import httpx
import websocket
from PIL import Image

canvas = {
    0: "🌎· Earth",
    1: "🌜· Moon",
    2: "🧱· 3D Canvas",
    3: "🦠· Coronavirus",
    7: "🔲· 1bit",
    8: "🏆· Top10",
}

canvas_convert = {"e": "0", "m": "1", "1": "7"}

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

class Pixelplanet:
    async def get_online() -> list:
        ws = websocket.create_connection("wss://pixelplanet.fun/ws")

        while True:
            data = ws.recv()
            if type(data) != str:
                online = []
                opcode = data[0]
                if opcode == 0xA7:
                    off = len(data)
                    while off > 3:
                        off -= 2
                        first = off
                        off -= 1
                        second = off
                        online.insert(
                            int(data[second]),
                            f"{canvas[int(data[second])]}: {str(int((data[first] << 8) | data[first + 1]))}",
                        )
                    online.insert(0, f"🌎 **Total**: {str((data[1] << 8) | data[2])}\n")

                    break

        ws.close()
        return online

    async def get_daily() -> list:
        players = []
        data = httpx.get("https://pixelplanet.fun/ranking").json()
        for i in range(100):
            player = data["dailyRanking"][i]
            players.append(player)

        return players

    async def get_ranking() -> list:
        players = []
        data = httpx.get("https://pixelplanet.fun/ranking").json()
        for i in range(100):
            player = data["ranking"][i]
            players.append(player)

        return players


class PlanetHistory:
    def __init__(self, canvas, start, filename, day, month, year):
        self.canvas = canvas_convert[canvas]
        self.day = day
        self.month = month
        self.year = year
        self.imgs = []

        template = TemplateSt()

        img = Image.open(f"{filename}").convert("RGBA")
        size = img.size

        me = httpx.get("https://pixelplanet.fun/api/me").json()
        csz = me["canvases"][self.canvas]["size"]
        ch = csz // 2

        self.start_y = (ch + int(start[1])) // 256
        self.start_x = (ch + int(start[0])) // 256
        self.last_y = ((ch + int(start[1]) + size[0]) // 256) + 1
        self.last_x = ((ch + int(start[0]) + size[1]) // 256) + 1

    async def get_history_chunk(self, client, x: int, y: int, time: str, img) -> None:
        time = time if not time == "tile" else "tiles"
        resp = await client.get(
            f"https://storage.pixelplanet.fun/{self.year}/{self.month}/{self.day}/{self.canvas}/{time}/{str(x)}/{str(y)}.png"
        )

        if resp.status_code == 200:
            img.paste(
                Image.open(BytesIO(resp.content)),
                (256 * (x - self.start_x), 256 * (y - self.start_y)),
            )
        template.madeChunks = template.madeChunks + 1
        if template.percentage() > template.thispc:
            template.thisPercentage()
            await inter.edit_original_message(f'Getting chunks for template {tempName}: {template.madeChunks}/{template.totalChunks} ({round(template.percentage())}%)\n[{"🟩"*(round(template.percentage()/10))}{"🟥"*(10-round(template.percentage()/10))}]')
        

    async def get_chunks_blob(self, time) -> None:
        await inter.response.send_message(f"Getting your fresh chunks: 0/{template.totalChunks} (0%)\n[{'🟥'*10}]")
        async with httpx.AsyncClient() as client:
            tasks = []
            img = Image.new(
                "RGBA",
                (
                    256 * (self.last_x - self.start_x),
                    256 * (self.last_y - self.start_y),
                ),
                (255, 0, 0, 0),
            )

            for y_index in range(self.start_y, self.last_y):
                for x_index in range(self.start_x, self.last_x):
                    template.totalChunks = template.totalChunks + 1
                    tasks.append(
                        asyncio.ensure_future(
                            self.get_history_chunk(client, x_index, y_index, time, img)
                        )
                    )
            await asyncio.gather(*tasks)
            self.imgs.append(img)
            await inter.edit_original_message(f"Getting your fresh chunks: {template.totalChunks}/{template.totalChunks} (100%)\n[{'🟩'*10}] \nChunks processed.\nMaking your gif")

    async def make_images(self) -> None:
        start = time.time()
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"https://pixelplanet.fun/history?day={self.year}{self.month}{self.day}&id=0"
            )
            tasks = []
            if resp.status_code == 200:
                times = resp.json()
                for i in times:
                    tasks.append(asyncio.ensure_future(self.get_chunks_blob(i)))

                await asyncio.gather(*tasks)

                await self.save_gif()
                return time.time() - start

    async def save_gif(self) -> None:
        async with httpx.AsyncClient() as client:
            tasks = []
            img = Image.new(
                "RGBA",
                (
                    256 * (self.last_x - self.start_x),
                    256 * (self.last_y - self.start_y),
                ),
                (255, 0, 0, 0),
            )

            for y_index in range(self.start_y, self.last_y):
                for x_index in range(self.start_x, self.last_x):
                    tasks.append(
                        asyncio.ensure_future(
                            self.get_history_chunk(
                                client, x_index, y_index, "tile", img
                            )
                        )
                    )

            await asyncio.gather(*tasks)
            img.save(
                "teste.gif",
                save_all=True,
                append_images=self.imgs,
                optimize=True,
                duration=80,
                loop=0,
            )
