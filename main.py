import discord
from discord.ext import commands
import os


TOKEN = os.environ.get("TOKEN")


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

initial_extensions = ['cogs.auth_commands', 'cogs.material_commands', 'cogs.groups_commands', 'cogs.bot_commands']


@bot.event
async def on_ready():
    print(f'Zalogowano jako {bot.user.name}')
    for extension in initial_extensions:
        await bot.load_extension(extension)


if __name__ == "__main__":
    bot.run(TOKEN)

