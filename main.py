import discord
from discord.ext import commands

def get_settings():
    settings = {}
    try:
        with open('data.txt', 'r') as file:
            for line in file:
                if line.startswith('TOKEN='):
                    settings['TOKEN'] = line.strip().split('=')[1]
                elif line.startswith('ADMINUSER='):
                    settings['ADMINUSER'] = line.strip().split('=')[1]
                elif line.startswith('ADMIN_SERVER='):
                    settings['ADMIN_SERVER'] = line.strip().split('=')[1]
                elif line.startswith('ROLE_NAME='):
                    settings['ROLE_NAME'] = line.strip().split('=')[1]
    except FileNotFoundError:
        print("Not data.txt")
    return settings

settings = get_settings()
ROLE_NAME = settings.get('ROLE_NAME')

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.guild_messages = True
intents.guild_reactions = True
intents.guild_scheduled_events = True
intents.members = True

client = commands.Bot(command_prefix='/', intents=intents)

@client.event
async def on_ready():
    print(f'Longin Success!: {client.user}')

TOKEN = settings.get('TOKEN')
if TOKEN:
    client.run(TOKEN)
else:
    print("TOKEN not set")
