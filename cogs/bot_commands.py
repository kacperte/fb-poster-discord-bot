from discord.ext import commands
from utils.file_utils import *
from utils.auth_utils import *
from dotenv import load_dotenv
import os
from utils.cache_singleton import CacheSingleton


cache_instance = CacheSingleton()
cache = cache_instance.cache


load_dotenv()

URL = os.getenv("URL")


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


async def setup(bot):
    print("BotCommands Cog loading...")
    cog = BotCommands(bot)
    await bot.add_cog(cog)
    print("BotCommands Cog loaded.")