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


class MaterialCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def getAllMaterials(self, ctx):
        """
        Retrieves and displays all materials from the database.
        Usage: !getAllMaterials
        No arguments required.
        Displays a list of all materials with details such as material ID, client, position, image name, text name, and author.
        ---
        Pobiera i wyświetla wszystkie materiały z bazy danych.
        Użycie: !getAllMaterials
        Nie wymaga argumentów.
        Wyświetla listę wszystkich materiałów wraz ze szczegółami takimi jak ID materiału, klient, stanowisko, nazwa grafiki, nazwa tekstu i autor.
        """

        headers = await check_login_and_get_headers(ctx, cache)
        if headers is None:
            return

        api_endpoint = urljoin(URL, "material")
        materials = await make_api_request(ctx, api_endpoint, headers)
        print(materials)
        if len(materials) ==0:
            await ctx.send("Nie dodano jeszcze żadnego materiału.")
            return

        material_strings = []

        for material in materials:
            material_str = (f":file_folder: **Material ID**: {material['id']}\n"
                            f":bust_in_silhouette: **Klient**: {material['client']}\n"
                            f":office: **Stanowisko**: {material['position']}\n"
                            f":frame_photo: **Nazwa grafiki**: {material['image_name']}\n"
                            f":page_facing_up: **Nazwa copy**: {material['text_name']}\n"
                            f":pencil: **Autor**: {material['user']['username']}\n")
            material_strings.append(material_str)

        await ctx.send("\n---\n".join(material_strings))

    @commands.command()
    async def getMaterial(self, ctx, id):
        """
        Fetches and displays a specific material by ID.
        Usage: !getMaterial <id>
        Arguments:
        - id: The unique identifier of the material to retrieve.
        Displays the material's details including client, project, and author along with the image and text content.
        ---
        Pobiera i wyświetla konkretny materiał na podstawie ID.
        Użycie: !getMaterial <id>
        Argumenty:
        - id: Unikalny identyfikator materiału do pobrania.
        Wyświetla szczegóły materiału, w tym klienta, projekt i autora wraz z obrazem i treścią tekstu.
        """

        headers = await check_login_and_get_headers(ctx, cache)
        if headers is None:
            return

        api_endpoint = urljoin(URL, f"material/{id}")

        material = await make_api_request(ctx, api_endpoint, headers)
        if material is None:
            return

        raw_image = get_from_gcp_storage(file_name=material['image_name'], bucket_name='fb-poster-storage')
        raw_text = get_from_gcp_storage(file_name=material['text_name'], bucket_name='fb-poster-storage')

        image = get_image(raw_image)
        text = get_txt(raw_text)

        title = f"**Klient**: {material['client']}\n**Projekt**: {material['position']} \n**Autor**: {material['user']['username']}"

        await ctx.send(title, file=image)

        await ctx.send(f"```{text}```")

    @commands.command()
    async def createMaterial(self, ctx, client, position):
        """
        Creates a new material with the specified client and position.
        Usage: !createMaterial <client> <position>
        Arguments:
        - client: The client's name.
        - position: The position or designation of the material.
        Creates a new material entry in the database and returns its ID.
        ---
        Tworzy nowy materiał z określonym klientem i stanowiskiem.
        Użycie: !createMaterial <klient> <stanowisko>
        Argumenty:
        - klient: Nazwa klienta.
        - stanowisko: Pozycja lub oznaczenie materiału.
        Tworzy nowy wpis materiału w bazie danych i zwraca jego ID.
        """

        txt_like_object, image_like_object = await handle_image_and_text_attachments(ctx, ctx.message.attachments)
        if txt_like_object is None or image_like_object is None:
            return

        search_string = f"{client}__{position}"
        matching_files = [file for file in list_files_in_bucket() if search_string in file]

        if matching_files:
            await ctx.send(f"😢 Materiał o takiej nazwie znadjuje się już w bazie. Wybierz inną nazwę lub zaktualizuj już istniejącą.")
            return

        headers = await check_login_and_get_headers(ctx, cache)
        if headers is None:
            return

        api_endpoint = urljoin(URL, f"material/?client={client}&position={position}")
        files = {
            'image': ('5.jpg', image_like_object.read(), 'image/jpeg'),
            'text_content': ('5.txt', txt_like_object.read(), 'text/plain')
        }
        response_dict = await make_api_request(ctx, api_endpoint, headers, method='POST', files=files)

        if response_dict is not None:
            await ctx.send(f"Nowy materiał o id {response_dict['id']} dodany do bazy. :+1:")

    @commands.command()
    async def updateMaterial(self, ctx, id, client, position):
        """
        Updates an existing material's details.
        Usage: !updateMaterial <id> <client> <position>
        Arguments:
        - id: The ID of the material to update.
        - client: The new client's name.
        - position: The new position or designation of the material.
        Updates the specified material and confirms the update.
        ---
        Aktualizuje szczegóły istniejącego materiału.
        Użycie: !updateMaterial <id> <klient> <stanowisko>
        Argumenty:
        - id: ID materiału do aktualizacji.
        - klient: Nowa nazwa klienta.
        - stanowisko: Nowa pozycja lub oznaczenie materiału.
        Aktualizuje określony materiał i potwierdza aktualizację
        """

        txt_like_object, image_like_object = await handle_image_and_text_attachments(ctx, ctx.message.attachments)
        if txt_like_object is None or image_like_object is None:
            return

        headers = await check_login_and_get_headers(ctx, cache)
        if headers is None:
            return

        api_endpoint = urljoin(URL, f"material/{id}?client={client}&position={position}")
        files = {
            'image': ('5.jpg', image_like_object.read(), 'image/jpeg'),
            'text_content': ('5.txt', txt_like_object.read(), 'text/plain')
        }
        response_dict = await make_api_request(ctx, api_endpoint, headers, method='PUT', files=files)

        if response_dict is not None:
            await ctx.send(f"Materiał o id {response_dict['id']} został zaktualizowany. :+1:")

    @commands.command()
    async def deleteMaterial(self, ctx, id):
        """
        Deletes a specific material from the database.
        Usage: !deleteMaterial <id>
        Arguments:
        - id: The unique identifier of the material to delete.
        Removes the specified material and confirms its deletion.
        ---
        Usuwa konkretny materiał z bazy danych.
        Użycie: !deleteMaterial <id>
        Argumenty:
        - id: Unikalny identyfikator materiału do usunięcia.
        Usuwa określony materiał i potwierdza jego usunięcie.
        """

        headers = await check_login_and_get_headers(ctx, cache)
        if headers is None:
            return

        api_endpoint = urljoin(URL, f"material/delete/{id}")
        response_dict = await make_api_request(ctx, api_endpoint, headers, method='DELETE')

        if response_dict is not None:
            await ctx.send(f"Materiał o id {response_dict['id']} został usunięty. :+1:")


async def setup(bot):
    print("MaterialCommands Cog loading...")
    cog = MaterialCommands(bot)
    await bot.add_cog(cog)
    print("MaterialCommands Cog loaded.")
