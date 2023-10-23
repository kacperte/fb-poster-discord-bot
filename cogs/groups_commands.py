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


class GroupsCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def getAllGroups(self, ctx):
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

        await ctx.send("\n---\n".join(groups_strings))

    @commands.command()
    async def getGroup(self, ctx, group_name):
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