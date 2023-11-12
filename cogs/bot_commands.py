from discord.ext import commands
from utils.file_utils import *
from utils.auth_utils import *
import os
from utils.cache_singleton import CacheSingleton
from utils.gsheets_utils import *


cache_instance = CacheSingleton()
cache = cache_instance.cache

with open('/tmp/adres-ip', 'r') as file:
    ip = file.read().strip()

URL = f'http://{ip}/'


class BotCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def runBot(self, ctx, groups_name, material_id):
        headers = await check_login_and_get_headers(ctx, cache)
        if headers is None:
            return

        data = {
            "login": cache[ctx.author]['username'],
            "password": cache[ctx.author]['password'],
            "email": cache[ctx.author]['username'],
            "groups_name": groups_name,
            "material_id": int(material_id)
        }

        api_endpoint = urljoin(URL, "bot/run")
        response_dict = await make_api_request(ctx, api_endpoint, method='POST', json=data)
        if response_dict is None:
            return

        if response_dict is not None:
            await ctx.send(f"Zostało uruchomione nowe zadanie do wykonania.")

    @commands.command()
    async def addNewTask(self, ctx, groups_name, material_id, day_of_the_week, info):
        headers = await check_login_and_get_headers(ctx, cache)
        if headers is None:
            return

        response = add_new_job_to_sheet(int(day_of_the_week), material_id, cache[ctx.author]['username'], groups_name, info)
        if isinstance(response, str):
            await ctx.send(response)
        elif isinstance(response, tuple):
            message, other_days_info = response
            await ctx.send(f"Nie można dodać nowego zadania: {message}")
            for info in other_days_info:
                await ctx.send(info)


async def setup(bot):
    print("BotCommands Cog loading...")
    cog = BotCommands(bot)
    await bot.add_cog(cog)
    print("BotCommands Cog loaded.")