import discord
from discord.ext import commands
import asyncio

def get_settings():
    settings = {}
    try:
        with open('data.txt', 'r', encoding='utf-8') as file:
            for line in file:
                if line.startswith('TOKEN='):
                    settings['TOKEN'] = line.strip().split('=')[1]
                elif line.startswith('ADMIN_SERVER='):
                    settings['ADMIN_SERVER'] = line.strip().split('=')[1]
                elif line.startswith('ROLE_NAME='):
                    settings['ROLE_NAME'] = line.strip().split('=')[1]
    except FileNotFoundError:
        print("data.txt not found")
    return settings

settings = get_settings()
TOKEN = settings.get('TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.guild_messages = True
intents.guild_reactions = True
intents.guild_scheduled_events = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print('Bot is ready and running!')

async def main():
    async with bot:
        await bot.load_extension('admin')
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
