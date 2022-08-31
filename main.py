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

print(f'[CONSOLE] Loaded prefix as: {prefix}.')
#config do bote
client = commands.Bot(command_prefix = f"{prefix}")
#disnake presence. se o bot for banido por causa de erros, mudar isso pra uma task async

class MyClient(disnake.Client):
    async def on_ready(self):
        print(f'[CONSOLE] Bot started.')

@client.event
async def on_ready():
    await client.change_presence(status=disnake.Status.online, activity=disnake.Game(name=f"Running on {len(client.guilds)} factions!"))
    print(client.guilds)
    print(f'[CONSOLE] Bot running!')

#só pra logging
@client.event
async def on_guild_remove(guild):
    print("[CONSOLE] Kicked from guild '{0.name}' (ID: {0.id})".format(guild))

#comando quase inutil
#@client.event
#async def on_message(message):
    #if ' phi ' in message.content.lower() or ' phi' in message.content.lower() or 'phi ' in message.content.lower() or 'phi' == message.content.lower():
        #await message.add_reaction('🤔')
    #if message.author.bot:
        #return
    #await client.process_commands(message)

@client.event
async def on_guild_join(guild):
    #Configuração inicial pra cada server. Neccessário que rodem o comando de configuração
    print(f"[CONSOLE] Joined new guild '{guild.name}' (ID: {guild.id})")
    repeated = False
    
    for i in os.listdir('factions/'):
        if i.startswith(f'{guild.id}'):
            print('[CONSOLE] This faction already exists.')
            repeated = True
        else:
            pass
    if repeated == False:
        os.mkdir(f'factions/{guild.id}_{guild.name}')
        print(f'[CONSOLE] Created a new faction {guild.name} (ID: {guild})')
    await print_welcome_message(guild)

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f'You have to wait {error.retry_after:.1f} seconds before using that command again.')
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f'Seems like this command doesn\'t exist, try using {prefix}help')
    if isinstance(error, commands.CommandInvokeError):
        await ctx.send(f'Command has raised a weird exception. Please notify @nisano#2763')
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f'Only admins of a server can remove the template. And you don\'t seem to be one. (no ban_members permissions)', file=disnake.File('noperms.gif'))

@client.command()
@commands.is_owner()
async def rena(ctx, name):
    await client.user.edit(username=name)
    print(f'[CONSOLE] Renamed! New bot name is {name}')

initial_extensions = [("cogs." + filename[:-3]) for filename in os.listdir('./Cogs')]

if __name__ == '__main__':
    for extension in initial_extensions:
        if extension.startswith('cogs.__pycach'):
            pass
        else:
            client.load_extension(extension)
    print('[CONSOLE] All cogs loaded.')

async def print_welcome_message(guild):
    #yes this is straight from starlight glimmer
    """Print a welcome message when joining a new server."""
    channels = (x for x in guild.channels if x.permissions_for(guild.me).send_messages and type(x) is TextChannel)
    c = next((x for x in channels if x.name == "general"), next(channels, None))
    if c:
        await c.send("I'm {0}. If you need any help: `{1}help` or @nisano#2763. "
                     "Supporting only PixelPlanet. Hosted on PebbleHost. ".format(bot_name, prefix))
        print("[CONSOLE] Printed welcome message")
    else:
        print("[CONSOLE] Could not print welcome message: no default channel found")


client.run(token)
