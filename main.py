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
ROLE_NAME = settings.get('ROLE_NAME')
ADMIN_SERVER = int(settings.get('ADMIN_SERVER'))

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

    await bot.load_extension('admin')
    try:
        await bot.tree.sync()
        print("Commands synced successfully.")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.tree.command(name="ping", description="Pong! Shows the bot's latency.")
async def ping(interaction: discord.Interaction):
    latency = interaction.client.ws.latency * 1000
    await interaction.response.send_message(f"Pong! Latency is {latency:.2f}ms")

    @discord.app_commands.command(name="msg", description="Send a message to the channel where the command was executed.")
    async def msg(self, interaction: discord.Interaction, *, message: str):
        await interaction.channel.send(message)

        success_message = await interaction.response.send_message("Success", ephemeral=True)
        
        await asyncio.sleep(1)
        try:
            messages = await interaction.channel.history(limit=2).flatten()
            for msg in messages:
                if msg.author == self.bot.user and msg.content == "Success":
                    await msg.delete()
                    break
        except discord.HTTPException as e:
            print(f"Failed to delete success message: {e}")

bot.run(TOKEN)
