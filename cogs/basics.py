from xmlrpc import client
import disnake
from disnake.ext import commands
from disnake.ext.commands import Command, HelpCommand
from discord_components import DiscordComponents, ComponentsBot, Button
import os
class Basics(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.slash_command(description='Answers the bot\'s invite to be shared')
    async def invite(self, inter: disnake.ApplicationCommandInteraction, template: str):
        await inter.response.send_message('Invite PHI with https://discord.com/api/oauth2/authorize?client_id=944655646157066280&permissions=0&scope=bot', file=disnake.File('giphy.gif'))

    @invite.autocomplete("template")
    async def template_autocomp(self, inter: disnake.ApplicationCommandInteraction, string: str):
        LANGUAGES = [f"{inter.guild.id}", f"{inter.guild.name}","typescript", "java", "rust", "lisp", "elixir"]
        string = string.lower()
        return [lang for lang in LANGUAGES if string in lang.lower()]

    @commands.cooldown(1, 5)
    @commands.command()
    async def button(self, ctx):
        await ctx.channel.send("Hello, World!", components = [Button(label = "WOW button!", custom_id = "button1")],)
        interaction = await self.client.wait_for("button_click", check = lambda i: i.custom_id == "button1")
        await interaction.respond(content = "Button clicked!", ephemeral=False)
    @commands.slash_command()
    async def canvaslist(self, ctx):
        await inter.response.send_message("Canvas list: \n'e':earth \n'1':1bit \n'm':moon")
    
    @commands.slash_command()
    async def setup(self, inter: disnake.ApplicationCommandInteraction, name: str):
        if '_' in name:
            await inter.response.send_message("Sorry you can't use underline (_) in your faction name.")
        else:
            newpath = f'./factions/{inter.guild.id}_{name}' 
            prefixed = [filename for filename in os.listdir('./factions/') if filename.startswith(f"{inter.guild.id}")]
            if len(prefixed) == 0:
                if not os.path.exists(newpath):
                    os.makedirs(newpath)
                    inter.response.send_message("👍 You can use the bot now!")
                else:
                    inter.response.send_message("Looks like you've already setup your faction! If it's still not working, notify <@919189528965709875>")
            else:
                await inter.response.send_message(f"This server already has a faction named {[filename for filename in os.listdir('./factions/') if filename.startswith(f'{inter.guild.id}')][0]} \nTo change your faction's name use p!setupchange")
    @commands.slash_command(description="Changes your faction name")
    async def setupchange(self, inter: disnake.ApplicationCommandInteraction, name: str):
        if '_' in name:
            await inter.response.send_message("Sorry you can't use underline (_) in your faction name.")
        else:
            prefixed = [filename for filename in os.listdir('./factions/') if filename.startswith(f"{ctx.message.guild.id}")]
            os.rename(f'./factions/{prefixed[0]}',f'./factions/{inter.guild.id}_{name}')
            await inter.response.send_message(f'Faction name changed to {name} succesfully')
    @commands.command()
    @commands.is_owner()
    async def reload(ctx, extension):
        bot.reload_extension(f"cogs.{extension}")
        embed = discord.Embed(title='Reload', description=f'{extension} successfully reloaded', color=0xff00c8)
        await ctx.send(embed=embed)
def setup(client):
    client.add_cog(Basics(client))