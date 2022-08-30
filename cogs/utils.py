from funcs.planet import *
from funcs.paginator import *

import disnake
from disnake.ext import commands


class Utils(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.cooldown(1, 5)
    @commands.slash_command()
    async def online(self, inter: disnake.ApplicationCommandInteraction):
        text = ""
        online = await Pixelplanet.get_online()

        for i in online:
            text += i + "\n"

        embed = disnake.Embed(color=0xFF0000)
        embed.set_author(
            name="Online",
            icon_url="https://imgs.search.brave.com/fmspp-a8_pNrkOHAPi-HMfOFc_UfS0Pyc2lkHN5B8qQ/rs:fit:256:256:1/g:ce/aHR0cHM6Ly9leHRl/cm5hbC1wcmV2aWV3/LnJlZGQuaXQvUVhp/ejlLT0o1ODJFUlNw/MjNOWHVpSldzNjVS/dVRNa2JLWU1vbGx1/emNHVS5qcGc_YXV0/bz13ZWJwJnM9Zjdk/NjY0ZTJmNDM3OGI2/YjM2ZmFkMmY3M2U0/OTA1Y2U0MzU4NmVl/ZA",
        )
        embed.description = text

        await inter.response.send_message(embed=embed)

    @commands.cooldown(1, 5)
    @commands.slash_command()
    async def daily(self, inter: disnake.ApplicationCommandInteraction, page: int = 1):
        embeds = []
        ranking = await Pixelplanet.get_daily()

        for j in range(0, 10):
            text = ""

            for i in range(0, 10):
                index = (j * 10) + i
                text += f"#{ranking[index]['dailyRanking']} {ranking[index]['name']}: {ranking[index]['dailyTotalPixels']}px\n "

            embed = disnake.Embed(color=0x42F57E)
            embed.set_author(
                name="Daily leaderboard",
                icon_url="https://imgs.search.brave.com/fmspp-a8_pNrkOHAPi-HMfOFc_UfS0Pyc2lkHN5B8qQ/rs:fit:256:256:1/g:ce/aHR0cHM6Ly9leHRl/cm5hbC1wcmV2aWV3/LnJlZGQuaXQvUVhp/ejlLT0o1ODJFUlNw/MjNOWHVpSldzNjVS/dVRNa2JLWU1vbGx1/emNHVS5qcGc_YXV0/bz13ZWJwJnM9Zjdk/NjY0ZTJmNDM3OGI2/YjM2ZmFkMmY3M2U0/OTA1Y2U0MzU4NmVl/ZA",
            )
            embed.description = text
            embeds.append(embed)

        if page > 10:
            await inter.response.send_message("The limit is 10.")
        else:
            await inter.response.send_message(
                embed=embeds[page - 1], view=Menu(embeds, inter.author, page)
            )

    @commands.cooldown(1, 5)
    @commands.slash_command()
    async def total(self, inter: disnake.ApplicationCommandInteraction, page: int = 1):
        embeds = []
        ranking = await Pixelplanet.get_ranking()

        for j in range(0, 10):
            text = ""

            for i in range(0, 10):
                index = (j * 10) + i
                text += f"#{ranking[index]['ranking']} {ranking[index]['name']}: {ranking[index]['totalPixels']}px\n "

            embed = disnake.Embed(color=0x5F62E3)
            embed.set_author(
                name="Total leaderboard",
                icon_url="https://imgs.search.brave.com/fmspp-a8_pNrkOHAPi-HMfOFc_UfS0Pyc2lkHN5B8qQ/rs:fit:256:256:1/g:ce/aHR0cHM6Ly9leHRl/cm5hbC1wcmV2aWV3/LnJlZGQuaXQvUVhp/ejlLT0o1ODJFUlNw/MjNOWHVpSldzNjVS/dVRNa2JLWU1vbGx1/emNHVS5qcGc_YXV0/bz13ZWJwJnM9Zjdk/NjY0ZTJmNDM3OGI2/YjM2ZmFkMmY3M2U0/OTA1Y2U0MzU4NmVl/ZA",
            )
            embed.description = text
            embeds.append(embed)

        if page > 10:
            await inter.response.send_message("The limit is 10.")
        else:
            await inter.response.send_message(
                embed=embeds[page - 1], view=Menu(embeds, inter.author, page)
            )


def setup(client):
    client.add_cog(Utils(client))