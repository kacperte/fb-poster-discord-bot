from discord.ext import commands
import os
import psycopg2
from datetime import datetime
import discord

TOKEN = os.environ.get("TOKEN")
CHANNEL_ID = 1190222508671107153

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)


def fetch_data():
    db_name = "postgres"
    db_user = "postgres"
    db_password = "postgres"
    db_host = "db-service"  
    db_port = "5432"

    try:
        conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        )

        cur = conn.cursor()

        today = datetime.now().date()

        query = "SELECT groups_to_procced FROM job_status WHERE date::date = %s"

        cur.execute(query, (today,))

        results = cur.fetchall()

        cur.close()
        conn.close()

        return results

    except Exception as e:
        print(f"Błąd podczas łączenia z bazą danych: {e}")
        return None


def format_output(data):
    output = []

    for task_number, group in enumerate(data, 1):
        total_urls = len(group)
        total_processed = sum(status == 'processed' for status in group.values())
        crashed_urls = [url for url, status in group.items() if status == 'crashed']
        not_a_member_urls = [url for url, status in group.items() if status == 'not-a-member']

        output.append(f"**Zadanie {task_number}.**")
        output.append(f"Ilość Grup: {total_urls} / Dodano: {total_processed}")

        if crashed_urls:
            output.append("**Błąd:**")
            for idx, url in enumerate(crashed_urls, 1):
                output.append(f"{idx}. {url}")

        if not_a_member_urls:
            output.append("**Dodano do grup:**")
            for idx, url in enumerate(not_a_member_urls, 1):
                output.append(f"{idx}. {url}")

        output.append("")  
    return "\n".join(output)


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
        data_dicts = [row[0] for row in data]
        format_message = format_output(data=data_dicts)
        await channel.send(format_message)
    else:
        await channel.send("Brak danych do wyświetlenia.")

    await bot.close()

bot.run(TOKEN)
