import disnake
from disnake.ext import commands
import time
import json
from PIL import Image, ImageChops
import requests
from io import BytesIO
from funcs import template, chunk, dataBase
import os
import matplotlib.pyplot as plt

class DiffButton(disnake.ui.View):
    def __init__(self, url):
        super().__init__()
        self.url = url 
        # Link buttons cannot be made with the decorator
        # Therefore we have to manually create one.
        # We add the quoted url to the button, and add the button to the view.
        self.add_item(disnake.ui.Button(label="Teleport", url=url))

    # When the confirm button is pressed, set the inner value to `True` and
    # stop the View from listening to more input.
    # We also send the user an ephemeral message that we're confirming their choice.
    @disnake.ui.button(label="Chunks", style=disnake.ButtonStyle.green, disabled=False)
    async def chunks(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        self.chunks.disabled = True
        await interaction.response.edit_message(view=self)
        embed=disnake.Embed(color=0xff0000)
        embed.set_author(name="Template chunks", icon_url="https://imgs.search.brave.com/fmspp-a8_pNrkOHAPi-HMfOFc_UfS0Pyc2lkHN5B8qQ/rs:fit:256:256:1/g:ce/aHR0cHM6Ly9leHRl/cm5hbC1wcmV2aWV3/LnJlZGQuaXQvUVhp/ejlLT0o1ODJFUlNw/MjNOWHVpSldzNjVS/dVRNa2JLWU1vbGx1/emNHVS5qcGc_YXV0/bz13ZWJwJnM9Zjdk/NjY0ZTJmNDM3OGI2/YjM2ZmFkMmY3M2U0/OTA1Y2U0MzU4NmVl/ZA")
        embed.set_thumbnail(url="https://cdn.discordapp.com/avatars/944655646157066280/95d8bee5622528bc2043982ace073924.png?size=256")
        embed.add_field(name="Chunks:", value="number of chunks", inline=False)
        embed.set_image(file=disnake.File("bigchunks.png"))
        embed.set_footer(text="sent at")
        await interaction.followup.send(embed=embed)
        #self.stop()

    # This one is similar to the confirmation button except sets the inner value to `False`
    @disnake.ui.button(label="Data", style=disnake.ButtonStyle.primary, disabled=False)
    async def data(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        self.data.disabled = True
        await interaction.response.edit_message(view=self)
        await interaction.followup.send("Cancelling",file=disnake.File('plot.png'))
        #self.stop()


class Diff(commands.Cog):
    def __init__(self, client):
        self.client = client
    @commands.Cog.listener("on_slash_command_error")
    async def error_handler(self, interaction, error):
        if isinstance(error, commands.CommandOnCooldown):
            await interaction.response.send_message(f'You have to wait {error.retry_after:.1f} seconds before using that command again.')
        if isinstance(error, commands.MissingPermissions):
            await interaction.response.send_message(f'Only admins of a server can remove the template. And you don\'t seem to be one. (no ban_members permissions)', file=disnake.File('noperms.gif'))
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
    @commands.cooldown(1, 5)
    @commands.slash_command()
    @commands.has_permissions(ban_members = True, kick_members = True)
    async def remove(self, inter: disnake.ApplicationCommandInteraction,name: str):
        await inter.response.send_message("Removed")

    @commands.cooldown(1, 15)
    @commands.slash_command()
    async def diff(self, inter: disnake.ApplicationCommandInteraction, name:str):
        userid = inter.guild.id
        username = inter.user.name
        print(f'[CONSOLE] Started Diff command for {username}: {name}')
        guildFolders = [filename for filename in os.listdir('./factions/') if filename.startswith(f"{inter.guild.id}")]
        templateArr = [temp.split('_') for temp in os.listdir(f'./factions/{guildFolders[0]}') if temp.endswith('.png') and temp.split('_')[1].startswith(f"{name}")]
        _n, tempName, x, y, canvas, fileFormat = templateArr[0]
        tot, err, elapsed = await chunk.compareImg(inter,[int(x),int(y)],f"./factions/{guildFolders[0]}/_{tempName}_{x}_{y}_{canvas}_{fileFormat}",tempName, 'diff')
        dataBase.writeNewNumeric(inter.guild.id, tempName, time.time(), (tot-err))
        print(f'[CONSOLE] Unpacking .csv data')
        d1, t1, d2, t2, d3, t3, d4, t4, d5, t5, d6, t6 = dataBase.readNumericData(inter.guild.id, tempName)
        print(d1,t1, d2, t2, d3, t3, d4, t4, d5, t5, d6, t6)
        pixel_rate = (d6-d5)/((t6-t5)/60/60)
        if pixel_rate == 0:
            expected_time = f'This is not going anywhere. 0 px/h'
        if pixel_rate > 0:
            expected_time = f'{(tot/pixel_rate) if (tot/pixel_rate) < 36 else (tot/pixel_rate/24):.2f} {"hours" if (tot/pixel_rate) < 36 else "days"}'
        if pixel_rate < 0:
            expected_time = f'{(tot/pixel_rate) if abs(tot/pixel_rate) < 36 else (tot/pixel_rate/24):.2f} {"hours" if abs(tot/pixel_rate) < 36 else "days"}'

        xx = [1,2,3,4,5,6]
        yy = [100*(d1/tot),100*(d2/tot),100*(d3/tot),100*(d4/tot),100*(d5/tot),100*(d6/tot)]
        plt.plot(xx,yy)
        plt.title(f'{tempName} percentage in the last 6 diffs')
        plt.savefig('plot.png')
        print('plot created')
        plt.close()
        print('plot closed')
        embed=disnake.Embed(title="Teleport to coordinates", url=f"https://www.pixelplanet.fun/#d,{x},{y},10", description=f"This took the bot {elapsed:.1f} seconds", color=0x00ff00)
        embed.set_author(name="Template progress", url="https://www.google.com.br/", icon_url="https://imgs.search.brave.com/fmspp-a8_pNrkOHAPi-HMfOFc_UfS0Pyc2lkHN5B8qQ/rs:fit:256:256:1/g:ce/aHR0cHM6Ly9leHRl/cm5hbC1wcmV2aWV3/LnJlZGQuaXQvUVhp/ejlLT0o1ODJFUlNw/MjNOWHVpSldzNjVS/dVRNa2JLWU1vbGx1/emNHVS5qcGc_YXV0/bz13ZWJwJnM9Zjdk/NjY0ZTJmNDM3OGI2/YjM2ZmFkMmY3M2U0/OTA1Y2U0MzU4NmVl/ZA")
        embed.set_thumbnail(url="https://cdn.discordapp.com/avatars/944655646157066280/95d8bee5622528bc2043982ace073924.png?size=256")
        embed.add_field(name="Placed / Needed", value=f"{tot - err:,} / {tot:,} ({100*((tot-err)/tot):.1f}%)", inline=True)
        embed.add_field(name="Errors", value=f"{err:,} ({d6-d5})", inline=False)
        embed.add_field(name="Pixel rate", value=f"{f'{round(pixel_rate)} px/h' if d5 != 0 else 'NaN px/h'}", inline=False)
        embed.add_field(name="Expected time at this rate", value=f"{expected_time}", inline=True)
        embed.set_footer(text=f"Last time this template was diffed: {time.ctime(t5)}")
        embed.set_image(file=disnake.File("difference.png"))
        view = DiffButton(f'https://www.pixelplanet.fun/#d,{x},{y},10')
        await inter.edit_original_message(embed=embed, view=view)
        await inter.wait()

    @commands.cooldown(1, 15)
    @commands.slash_command()
    async def virgin(self, inter:disnake.ApplicationCommandInteraction, name:str):
        userid = inter.guild.id
        username = inter.user.name
        guildFolders = [filename for filename in os.listdir('./factions/') if filename.startswith(f"{inter.guild.id}")]
        templateArr = [temp.split('_') for temp in os.listdir(f'./factions/{guildFolders[0]}') if temp.split('_')[1].startswith(f"{name}")]
        _n, tempName, x, y, canvas, fileFormat = templateArr[0]
        virginpixels, elapsed = await chunk.compareImg(inter,[int(x),int(y)],f"./factions/{guildFolders[0]}/_{tempName}_{x}_{y}_{canvas}_{fileFormat}",tempName, 'virgins')
        embed=disnake.Embed(title=f"{tempName}", url=f"https://www.pixelplanet.fun/#d,{x},{y},10", description=f"This took the bot {elapsed:.1f} seconds", color=0x00ff00)
        embed.set_author(name="Virgin pixels", url="https://www.google.com.br/", icon_url="https://imgs.search.brave.com/fmspp-a8_pNrkOHAPi-HMfOFc_UfS0Pyc2lkHN5B8qQ/rs:fit:256:256:1/g:ce/aHR0cHM6Ly9leHRl/cm5hbC1wcmV2aWV3/LnJlZGQuaXQvUVhp/ejlLT0o1ODJFUlNw/MjNOWHVpSldzNjVS/dVRNa2JLWU1vbGx1/emNHVS5qcGc_YXV0/bz13ZWJwJnM9Zjdk/NjY0ZTJmNDM3OGI2/YjM2ZmFkMmY3M2U0/OTA1Y2U0MzU4NmVl/ZA")
        embed.set_thumbnail(url="https://cdn.discordapp.com/avatars/944655646157066280/95d8bee5622528bc2043982ace073924.png?size=256")
        embed.add_field(name="Number of virgin pixels", value=f"{virginpixels:,}", inline=True)
        embed.set_image(file=disnake.File("virgins.png"))
        await inter.edit_original_message(embed=embed)

    @virgin.autocomplete("name")
    async def namecomplete(self, inter: disnake.ApplicationCommandInteraction,string: str):
        string = string.lower()
        guildFolders = [filename for filename in os.listdir('./factions/') if filename.startswith(f"{inter.guild.id}")]
        templates = [temp.split('_')[1] for temp in os.listdir(f'./factions/{guildFolders[0]}')]
        print(templates)
        return [lang for lang in templates if string in lang.lower()]
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
        templates = [temp.split('_')[1] for temp in os.listdir(f'./factions/{guildFolders[0]}') if temp.endswith('.png')]
        return [lang for lang in templates if string in lang.lower()]

def setup(client):
    client.add_cog(Diff(client))