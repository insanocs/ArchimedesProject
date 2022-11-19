import os
from configparser import ConfigParser

import disnake
from disnake import TextChannel
from disnake.ext import commands

#merda ipnicial
print(f"[CONSOLE] Starting.")
print(f"[CONSOLE] List of factions: {os.listdir('factions/')}.")
#configuraçoes

config = ConfigParser()
config.read(r'config.ini')
try:
    bot_name = config['BOTCONFIG']['name']
    token = config['BOTCONFIG']['token']
    auth_id = config['BOTCONFIG']['auth_id']
    prefix = config['BOTCONFIG']['prefix']
except:
    print('Error parsing config file')
    exit()

#config do bote
#disnake presence. se o bot for banido por causa de erros, mudar isso pra uma task async

class MyClient(disnake.ext.commands.Bot):

    async def on_ready(self):
        print('-'*10)
        print(f'[CONSOLE] Bot started as {self.user}. ID: {self.user.id}. Latency: {self.latency}. Prefix: "{prefix}"')
        print('-'*10)
        await self.change_presence(status=disnake.Status.online, activity=disnake.Game(name=f'-> discord.io/phibot <-'))
        #await self.change_presence(status=disnake.Status.online, activity=disnake.Game(name=f"We're back: -GIVE THE BOT 'Application commands' permissions. TYPE /setup (faction_name) BEFORE USING THE BOT"))

    #async def on_message(self, message):
        #if message.content.startswith("g!"):
        #    await message.add_reaction('🤔')
        #if ' phi ' in message.content.lower() or ' phi' in message.content.lower() or 'phi ' in message.content.lower() or 'phi' == message.content.lower():
        #    await message.add_reaction('🤔')
        #if message.author.bot:
        #    return
    async def on_guild_remove(self, guild):
        print("[CONSOLE] Kicked from guild '{0.name}' (ID: {0.id})".format(guild))

    async def on_guild_join(self, guild):
        #Configuração inicial pra cada server. Neccessário que rodem o comando de configuração
        print(f"[CONSOLE] Joined new guild '{guild.name}' (ID: {guild.id})")
        newpath = f'./factions/{guild.id}' 
        prefixed = [filename for filename in os.listdir('./factions/') if filename.startswith(f"{inter.guild.id}")]
        if len(prefixed) == 0:
            if not os.path.exists(newpath):
                os.makedirs(newpath)
                shutil.copy('_phi_-418_-21_e_.png', newpath)
                await inter.response.send_message("👍 You can use the bot now!")
            else:
                await inter.response.send_message("Looks like you've already setup your faction! If it's still not working, notify <@919189528965709875>")
        else:
            await inter.response.send_message(f"This server already has a faction named {[filename for filename in os.listdir('./factions/') if filename.startswith(f'{inter.guild.id}')][0]} \nTo change your faction's name use p!setupchange")
        await print_welcome_message(guild)

intents = disnake.Intents.default()
intents.members = False
intents.message_content = False
client = MyClient(command_prefix=prefix,intents=intents)

print('[CONSOLE] All cogs loaded.')

async def print_welcome_message(guild):
    #yes this is straight from starlight glimmer
    """Print a welcome message when joining a new server."""
    channels = (x for x in guild.channels if x.permissions_for(guild.me).send_messages and type(x) is TextChannel)
    c = next((x for x in channels if x.name == "general"), next(channels, None))
    if c:
        await c.send("I'm {0}. If you need any help: discord.io/phibot or @nisano#2763. "
                     "Supporting only PixelPlanet. Hosted on Square Cloud".format(bot_name, prefix))
        print("[CONSOLE] Printed welcome message")
    else:
        print("[CONSOLE] Could not print welcome message: no default channel found")

initial_extensions = [("cogs." + filename[:-3]) for filename in os.listdir('./cogs')]
for extension in initial_extensions:
    if extension.startswith('cogs.__pycach'):
        pass
    else:
        client.load_extension(extension)
client.run(token)
