import disnake
from disnake.ext import commands
import time
import json
from PIL import Image, ImageChops
import requests
from io import BytesIO
from funcs.template import saveTemplate
import os
class Diff(commands.Cog):
    def __init__(self, client):
        self.client = client
    @commands.cooldown(1, 5)
    @commands.command()
    async def add(self, ctx, name, canvas, x, y, *args):
        canvasList = ["e","1","m"]
        print(f'[CONSOLE] New template being added from: {ctx.guild.name}')
        #Checar se o comando tá certo
        if '_' in name:
            ctx.channel.send(f"Sorry. You can't use _(underline) in your template name.")
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
                        await ctx.channel.send(f"Coordinates can't be higher than 32768 or lower than -32768")
                    else:
                        try:
                            #checar modo da url
                            url = args[0]
                            print(f'[CONSOLE] Found url: {url}')
                            response = requests.get(url, stream=True)
                            img = Image.open(BytesIO(response.content)).convert('RGBA')
                            saveResult = saveTemplate(name, img, [str(x),str(y)], canvas, ctx.message.guild.id)
                            if saveResult == 0:
                                await ctx.channel.send("Seems like your faction still need a setup. Use p!setup (name)")
                            elif saveResult == 1:
                                await ctx.channel.send("Another template has already been created with that name.")
                            elif saveResult == 2:
                                await ctx.channel.send(f"Template successfully created as {name}")
                                print(f"Template created as {name} for {ctx.message.guild.id}")
                        except IndexError as e:
                            print('[EXPECTED ERROR] ' + e)
                            print('[CONSOLE] User template is attached.')
                            attachment = ctx.message.attachments[0]
                            url = attachment.url
                            response = requests.get(url, stream=True)
                            img = Image.open(BytesIO(response.content)).convert('RGBA')
                            saveResult = saveTemplate(name, img, [str(x),str(y)], canvas, ctx.message.guild.id)
                            if saveResult == 0:
                                await ctx.channel.send("Seems like your faction still need a setup. Use p!setup (name)")
                            elif saveResult == 1:
                                await ctx.channel.send("Another template has already been created with that name.")
                            elif saveResult == 2:
                                await ctx.channel.send(f"Template successfully created as {name}")
                                print(f"Template created as {name} for {ctx.message.guild.id}")
                except Exception as e:
                    await ctx.channel.send(f'X and Y arguments must be numbers. Try p!help  for more info')
                    print(f'[ERROR] X and Y arguments must be numbers. {e}')
                    return
            else:
                await ctx.channel.send(f'Unsupported canvas OR wrong usage of command. Type p!canvaslist or or p!help for more info.')
    @commands.command()
    @commands.has_permissions(ban_members = True, kick_members = True)
    async def remove(self,ctx,name):
        await ctx.channel.send('Voce tem permissoes agora viado')

        


def setup(client):
    client.add_cog(Diff(client))