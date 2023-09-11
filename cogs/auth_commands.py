from discord.ext import commands
from ..utils.auth_utils import get_credentials
from dotenv import load_dotenv
import os
from ..utils.cache_singleton import CacheSingleton

cache_instance = CacheSingleton()
cache = cache_instance.cache

load_dotenv()

URL = os.getenv("URL")


class AuthCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def setLogin(self, ctx, username: str, password: str):
        try:
            grant = get_credentials(URL=URL, login=username.strip(), password=password.strip())
        except ValueError as e:
            await ctx.send(str(e))
            return

        if username in cache:
            cache[ctx.author]['username'] = username
            cache[ctx.author]['password'] = password
            cache[ctx.author]['grant'] = grant
        else:
            cache[ctx.author] = {
                'username': username,
                'password': password,
                'grant': grant
            }
        await ctx.send(f"Zapisano dane dla {username}.")


def setup(bot):
    bot.add_cog(AuthCommands(bot))
