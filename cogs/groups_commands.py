from discord.ext import commands
from utils.file_utils import *
from utils.auth_utils import *
import os
from utils.cache_singleton import CacheSingleton


cache_instance = CacheSingleton()
cache = cache_instance.cache

with open('/tmp/adres-ip', 'r') as file:
    ip = file.read().strip()

URL = f'http://{ip}/'


class GroupsCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def getAllGroups(self, ctx):
        """
        Retrieves and displays all groups from the database.
        Usage: !getAllGroups
        No arguments required.
        Displays a list of all groups with details such as group ID, group name, and group list.
        ---
        Pobiera i wyświetla wszystkie grupy z bazy danych.
        Użycie: !getAllGroups
        Nie wymaga argumentów.
        Wyświetla listę wszystkich grup wraz ze szczegółami takimi jak ID grupy, nazwa grupy i lista grup.
        """

        headers = await check_login_and_get_headers(ctx, cache)
        if headers is None:
            await ctx.send("Nie dodano jeszcze żadnej grupy.")
            return

        api_endpoint = urljoin(URL, "groups")
        groups = await make_api_request(ctx, api_endpoint, headers)
        if len(groups) == 0:
            await ctx.send("Nie dodano jeszcze żadnych grup.")
            return

        groups_strings = []

        for group in groups:
            group_str = (f":file_folder: **ID Listy grup**: {group['id']}\n"
                            f":bust_in_silhouette: **Nazwa listy grup**: {group['groups_name']}\n"
                            f":office: **Lista grup**: ```{group['groups']}```\n"
                         )
            groups_strings.append(group_str)

        MAX_MESSAGE_LENGTH = 2000
        current_message = ""

        for material_str in groups_strings:
            if len(current_message) + len(material_str) + len("\n---\n") > MAX_MESSAGE_LENGTH:
                await ctx.send(current_message)
                current_message = material_str
            else:
                current_message += "\n---\n" + material_str

        if current_message:
            await ctx.send(current_message)

    @commands.command()
    async def getGroup(self, ctx, group_name):
        """
        Fetches and displays a specific group by its name.
        Usage: !getGroup <group_name>
        Arguments:
        - group_name: The name of the group to retrieve.
        Displays the group's details including group ID, group name, and the group list.
        ---
        Pobiera i wyświetla konkretną grupę na podstawie jej nazwy.
        Użycie: !getGroup <nazwa_grupy>
        Argumenty:
        - nazwa_grupy: Nazwa grupy do pobrania.
        Wyświetla szczegóły grupy, w tym ID grupy, nazwę grupy i listę grup.
        """

        headers = await check_login_and_get_headers(ctx, cache)
        if headers is None:
            return

        api_endpoint = urljoin(URL, f"groups/group/{group_name}")

        group = await make_api_request(ctx, api_endpoint, headers)
        if group is None:
            return

        group_str = (f":file_folder: **ID Listy grup**: {group['id']}\n"
                            f":bust_in_silhouette: **Nazwa listy grup**: {group['groups_name']}\n"
                            f":office: **Lista grup**: ```{group['groups']}```\n"
                         )

        await ctx.send(group_str)

    @commands.command()
    async def createGroup(self, ctx, groups_name):
        """
        Creates a new group with the specified name.
        Usage: !createGroup <groups_name>
        Arguments:
        - groups_name: The name for the new group.
        Creates a new group entry in the database and returns its ID.
        ---
        Tworzy nową grupę o określonej nazwie.
        Użycie: !createGroup <nazwa_grupy>
        Argumenty:
        - nazwa_grupy: Nazwa nowej grupy.
        Tworzy nowy wpis grupy w bazie danych i zwraca jej ID.
        """

        csv_like_object = await handle_csv_attachment(ctx, ctx.message.attachments)
        if csv_like_object is None:
            return

        headers = await check_login_and_get_headers(ctx, cache)
        if headers is None:
            return

        api_endpoint = urljoin(URL, f"groups/?groups_name={groups_name}")
        files = {
            'groups': ('5.csv', csv_like_object.read(), 'text/csv'),
        }
        response_dict = await make_api_request(ctx, api_endpoint, headers, method='POST', files=files)

        if response_dict is not None:
            await ctx.send(f"Nowa lista grup o id {response_dict['id']} dodany do bazy. :+1:")

    @commands.command()
    async def updateGroup(self, ctx, id, groups_name):
        """
        Updates an existing group's details.
        Usage: !updateGroup <id> <groups_name>
        Arguments:
        - id: The ID of the group to update.
        - groups_name: The new name for the group.
        Updates the specified group and confirms the update.
        ---
        Aktualizuje szczegóły istniejącej grupy.
        Użycie: !updateGroup <id> <nazwa_grupy>
        Argumenty:
        - id: ID grupy do aktualizacji.
        - nazwa_grupy: Nowa nazwa dla grupy.
        Aktualizuje określoną grupę i potwierdza aktualizację.
        """

        csv_like_object = await handle_csv_attachment(ctx, ctx.message.attachments)
        if csv_like_object is None:
            return

        headers = await check_login_and_get_headers(ctx, cache)
        if headers is None:
            return

        api_endpoint = urljoin(URL, f"groups/group/{id}?groups_name={groups_name}")
        files = {
            'groups': ('5.csv', csv_like_object.read(), 'text/csv'),
        }
        response_dict = await make_api_request(ctx, api_endpoint, headers, method='PUT', files=files)

        if response_dict is not None:
            await ctx.send(f"Lista grup o id {id} został zaktualizowana. :+1:")

    @commands.command()
    async def deleteGroup(self, ctx, groups_name):
        """
        Deletes a specific group from the database by name.
        Usage: !deleteGroup <groups_name>
        Arguments:
        - groups_name: The name of the group to delete.
        Removes the specified group and confirms its deletion.
        ---
        Usuwa konkretną grupę z bazy danych po nazwie.
        Użycie: !deleteGroup <nazwa_grupy>
        Argumenty:
        - nazwa_grupy: Nazwa grupy do usunięcia.
        Usuwa określoną grupę i potwierdza jej usunięcie.
        """

        headers = await check_login_and_get_headers(ctx, cache)
        if headers is None:
            return

        api_endpoint = urljoin(URL, f"groups/delete/{groups_name}")
        response_dict = await make_api_request(ctx, api_endpoint, headers, method='DELETE')

        if response_dict is not None:
            await ctx.send(f"Lista grup o nazwie {groups_name} został usunięta. :+1:")


async def setup(bot):
    print("GroupsCommands Cog loading...")
    cog = GroupsCommands(bot)
    await bot.add_cog(cog)
    print("GroupsCommands Cog loaded.")