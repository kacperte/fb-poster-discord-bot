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


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('Nie znaleziono komendy. Użyj `!help` aby zobaczyć dostępne komendy.')
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Brakuje wymaganego argumentu. Użyj `!help <komenda>` aby zobaczyć jak używać tej komendy.')
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send('Nie masz uprawnień do wykonania tej komendy.')
    else:
        print(f'Wystąpił nieoczekiwany błąd: {type(error).__name__} - {error}')


if __name__ == "__main__":

    bot.run(TOKEN)

