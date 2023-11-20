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
        """
        Executes a bot task for a specified group and material.
        Usage: !runBot <groups_name> <material_id>
        Arguments:
        - groups_name: The name of the group for which the task is to be run.
        - material_id: The ID of the material to be used for the task.
        Initiates a bot task using the specified group and material details.
        ---
        Uruchamia zadanie bota dla określonej grupy i materiału.
        Użycie: !runBot <nazwa_grupy> <id_materiału>
        Argumenty:
        - nazwa_grupy: Nazwa grupy, dla której ma być uruchomione zadanie.
        - id_materiału: ID materiału, który ma być użyty do zadania.
        Inicjuje zadanie bota z użyciem określonych szczegółów grupy i materiału.
        """

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
        """
        Adds a new task to the schedule for a specific group and material.
        Usage: !addNewTask <groups_name> <material_id> <day_of_the_week> <info>
        Arguments:
        - groups_name: The name of the group for which the task is to be added.
        - material_id: The ID of the material related to the task.
        - day_of_the_week: The day of the week the task is scheduled for (as a number).
        - info: Additional information about the task.
        Registers a new task in the schedule with the specified parameters.
        ---
        Dodaje nowe zadanie do harmonogramu dla konkretnej grupy i materiału.
        Użycie: !addNewTask <nazwa_grupy> <id_materiału> <dzień_tygodnia> <informacje>
        Argumenty:
        - nazwa_grupy: Nazwa grupy, dla której ma być dodane zadanie.
        - id_materiału: ID materiału związanego z zadaniem.
        - dzień_tygodnia: Dzień tygodnia, na który zaplanowano zadanie (jako liczba).
        - informacje: Dodatkowe informacje o zadaniu.
        Rejestruje nowe zadanie w harmonogramie z określonymi parametrami.
        """

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