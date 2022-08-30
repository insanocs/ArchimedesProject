import websocket
import httpx

canvas = {
    0: "🌎· Earth",
    1: "🌜· Moon",
    2: "🧱· 3D Canvas",
    3: "🦠· Coronavirus",
    7: "🔲· 1bit",
    8: "🏆· Top10",
}


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