from discord.ext import commands
from utils.db_utils import fetch_data
import os

TOKEN = os.environ.get("TOKEN")
CHANNEL_ID = 1144310082012709004

bot = commands.Bot(command_prefix='!')


@bot.event
async def on_ready():
    print(f'Zalogowano jako {bot.user}')
    await send_data_to_discord()


async def send_data_to_discord():
    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        print("Nie znaleziono kanału")
        return

    data = fetch_data()
    if data:
        message = "\n".join([str(row[0]) for row in data])
        await channel.send(message)
    else:
        await channel.send("Brak danych do wyświetlenia.")

    await bot.close()

bot.run(TOKEN)
