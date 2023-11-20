from discord.ext import commands
from utils.auth_utils import get_credentials
import os
from utils.cache_singleton import CacheSingleton


cache_instance = CacheSingleton()
cache = cache_instance.cache

with open('/tmp/adres-ip', 'r') as file:
    ip = file.read().strip()

URL = f'http://{ip}/'


class AuthCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def setLogin(self, ctx, username: str, password: str):
        """
        Sets the login credentials for the user.
        Usage: !setLogin <username> <password>
        Arguments:
        - username: The username to be set for the current user.
        - password: The password associated with the username.
        Stores the provided username and password in the cache and attempts to authenticate with the given credentials.
        On successful authentication, it saves the credentials for future requests.
        ---
        Ustawia dane logowania dla użytkownika.
        Użycie: !setLogin <nazwa_użytkownika> <hasło>
        Argumenty:
        - nazwa_użytkownika: Nazwa użytkownika, która ma być ustawiona dla bieżącego użytkownika.
        - hasło: Hasło powiązane z nazwą użytkownika.
        Przechowuje podaną nazwę użytkownika i hasło w pamięci podręcznej i próbuje uwierzytelnić się przy użyciu podanych
        poświadczeń. Po pomyślnym uwierzytelnieniu zapisuje poświadczenia na przyszłe żądania.
        """

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


async def setup(bot):
    print("AuthCommands Cog loading...")
    cog = AuthCommands(bot)
    await bot.add_cog(cog)
    print("AuthCommands Cog loaded.")

