import disnake
from disnake.ext import commands
import time
import json
from PIL import Image, ImageChops
import requests
from io import BytesIO
from funcs import template, chunk
import os
class Diff(commands.Cog):
    def __init__(self, client):
        self.client = client
    @commands.cooldown(1, 5)
    @commands.slash_command()
    async def add(self, inter: disnake.ApplicationCommandInteraction, name: str, canvas: str, x: int, y: int, image_link: str):
        canvasList = ["e","1","m"]
        print(f'[CONSOLE] New template being added from: {inter.guild.name}')
        #Checar se o comando tá certo
        if '_' in name:
            inter.response.send_message(f"Sorry. You can't use _(underline) in your template name.")
            print('[ERROR] User added template name with "_"(underline). Stopping operation')
        #Checar se o comando tem um canvas existente
        else:
            if canvas in canvasList:
                try:
                    #Checar se o comando tem x e y válidos
                    print(f'x:{x},y:{y}')
                    x = int(x)
                    y = int(y)
                    print(f'x:{type(x)},y:{type(y)}')
                    if abs(x) >> 32768 or abs(y) >> 32768:
                        await inter.response.send_message(f"Coordinates can't be higher than 32768 or lower than -32768")
                    else:
                        try:
                            #checar modo da url
                            url = image_link
                            print(f'[CONSOLE] Found url: {url}')
                            response = requests.get(url, stream=True)
                            img = Image.open(BytesIO(response.content)).convert('RGBA')
                            saveResult = template.saveTemplate(name, img, [str(x),str(y)], canvas, inter.guild.id)
                            if saveResult == 0:
                                await inter.response.send_message("Seems like your faction still need a setup. Use p!setup (name)")
                            elif saveResult == 1:
                                await inter.response.send_message("Another template has already been created with that name.")
                            elif saveResult == 2:
                                await inter.response.send_message(f"Template successfully created as {name}")
                                print(f"Template created as {name} for {inter.guild.id}")
                        except IndexError as e:
                            print('[EXPECTED ERROR] ' + e)
                            print('[CONSOLE] User template is attached.')
                            attachment = ctx.message.attachments[0]
                            url = attachment.url
                            response = requests.get(url, stream=True)
                            img = Image.open(BytesIO(response.content)).convert('RGBA')
                            saveResult = template.saveTemplate(name, img, [str(x),str(y)], canvas, inter.guild.id)
                            if saveResult == 0:
                                await inter.response.send_message("Seems like your faction still need a setup. Use p!setup (name)")
                            elif saveResult == 1:
                                await inter.response.send_message("Another template has already been created with that name.")
                            elif saveResult == 2:
                                await inter.response.send_message(f"Template successfully created as {name}")
                                print(f"Template created as {name} for {ctx.message.guild.id}")
                except Exception as e:
                    await inter.response.send_message(f'X and Y arguments must be numbers. Try p!help  for more info')
                    print(f'[ERROR] X and Y arguments must be numbers. {e}')
                    return
            else:
                await ctx.channel.send(f'Unsupported canvas OR wrong usage of command. Type p!canvaslist or or p!help for more info.')

    @commands.slash_command()
    @commands.has_permissions(ban_members = True, kick_members = True)
    async def remove(self, inter: disnake.ApplicationCommandInteraction,name: str):
        await inter.response.send_message("Removed")

    @commands.slash_command()
    @commands.has_permissions()
    async def diff(self, inter: disnake.ApplicationCommandInteraction, name:str):
        await inter.response.defer(with_message='Getting your fresh chunks...')
        userid = inter.guild.id
        username = inter.user.name
        guildFolders = [filename for filename in os.listdir('./factions/') if filename.startswith(f"{inter.guild.id}")]
        templateArr = [temp.split('_') for temp in os.listdir(f'./factions/{guildFolders[0]}') if temp.split('_')[1].startswith(f"{name}")]
        _n, tempName, x, y, canvas, fileFormat = templateArr[0]
        tot, err, elapsed = await chunk.compareImg(inter,[int(x),int(y)],f"./factions/{guildFolders[0]}/_{tempName}_{x}_{y}_{canvas}_{fileFormat}")
        embed=disnake.Embed(title="Teleport to coordinates", url=f"https://www.pixelplanet.fun/#d,{x},{y},10", description=f"This took the bot {elapsed:.1f} seconds", color=0x00ff00)
        embed.set_author(name="Template progress", url="https://www.google.com.br/", icon_url="https://imgs.search.brave.com/fmspp-a8_pNrkOHAPi-HMfOFc_UfS0Pyc2lkHN5B8qQ/rs:fit:256:256:1/g:ce/aHR0cHM6Ly9leHRl/cm5hbC1wcmV2aWV3/LnJlZGQuaXQvUVhp/ejlLT0o1ODJFUlNw/MjNOWHVpSldzNjVS/dVRNa2JLWU1vbGx1/emNHVS5qcGc_YXV0/bz13ZWJwJnM9Zjdk/NjY0ZTJmNDM3OGI2/YjM2ZmFkMmY3M2U0/OTA1Y2U0MzU4NmVl/ZA")
        embed.set_thumbnail(url="https://cdn.discordapp.com/avatars/944655646157066280/95d8bee5622528bc2043982ace073924.png?size=256")
        embed.add_field(name="Placed / Needed", value=f"{tot - err:,} / {tot:,} ({100*((tot-err)/tot):.1f}%)", inline=True)
        embed.add_field(name="Errors", value=f"{err:,}", inline=False)
        embed.add_field(name="Pixel rate", value="NaN PX/h", inline=False)
        embed.add_field(name="Expected time", value="NaN hours (if the same speed continues)", inline=True)
        embed.set_footer(text="Last time this template was diffed: NaN/NaN/NaN")
        embed.set_image(file=disnake.File("difference.png"))
        await inter.edit_original_message(embed=embed)


    @remove.autocomplete("name")
    async def namecomplete(self, inter: disnake.ApplicationCommandInteraction,string: str):
        string = string.lower()
        guildFolders = [filename for filename in os.listdir('./factions/') if filename.startswith(f"{inter.guild.id}")]
        templates = [temp.split('_')[1] for temp in os.listdir(f'./factions/{guildFolders[0]}')]
        print(templates)
        return [lang for lang in templates if string in lang.lower()]
    @diff.autocomplete("name")
    async def namecomplete(self, inter: disnake.ApplicationCommandInteraction,string: str):
        string = string.lower()
        guildFolders = [filename for filename in os.listdir('./factions/') if filename.startswith(f"{inter.guild.id}")]
        templates = [temp.split('_')[1] for temp in os.listdir(f'./factions/{guildFolders[0]}')]
        print(templates)
        return [lang for lang in templates if string in lang.lower()]


def setup(client):
    client.add_cog(Diff(client))