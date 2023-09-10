import discord
from discord.ext import commands
import requests
import json
from urllib.parse import urljoin
from scripts import *
import io


GUILD = "HSS Work"
URL = "http://34.118.109.108/"

intents = discord.Intents.default()
intents.message_content = True


bot = commands.Bot(command_prefix='!', intents=intents)

cache = dict()


@bot.event
async def on_ready():
    guild = discord.utils.find(lambda g: g.name == GUILD, bot.guilds)
    print(
        f'{bot.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )


@bot.command()
async def setLogin(ctx, username: str, password: str):
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


@bot.command()
async def getAllMaterial(ctx):
    headers = await check_login_and_get_headers(ctx, cache)
    if headers is None:
        return

    full_url = urljoin(URL, "material")
    try:
        response_token = requests.get(
            url=full_url,
            headers=headers,
        )
        response_token.raise_for_status()
    except requests.HTTPError as e:
        raise ValueError(f"Invalid credentials, HTTP status code: {e.response.status_code}")

    materials = json.loads(response_token.content)

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


@bot.command()
async def getMaterial(ctx, id):
    headers = await check_login_and_get_headers(ctx, cache)
    if headers is None:
        return

    full_url = urljoin(URL, f"material/{id}")
    try:
        response_token = requests.get(
            url=full_url,
            headers=headers,
        )
        response_token.raise_for_status()
    except requests.HTTPError as e:
        raise ValueError(f"Invalid credentials, HTTP status code: {e.response.status_code}")

    material = json.loads(response_token.content)

    raw_image = get_from_gcp_storage(file_name=material['image_name'], bucket_name='fb-poster-bucket')
    raw_text = get_from_gcp_storage(file_name=material['text_name'], bucket_name='fb-poster-bucket')

    image = get_image(raw_image)
    text = get_txt(raw_text)

    title = f"**Klient**: {material['client']}\n**Projekt**: {material['position']} \n**Autor**: {material['user']['username']}"

    await ctx.send(title, file=image)

    await ctx.send(f"```{text}```")


@bot.command()
async def createMaterial(ctx, client, position):
    if len(ctx.message.attachments) != 2:
        await ctx.send("😢 Dodaj dokładnie dwa pliki: jeden obraz (format .jpg) oraz jeden tekst (format .txt).")
        return

    txt_like_object = io.BytesIO()
    image_like_object = io.BytesIO()

    txt_attachment = None
    image_attachment = None

    for attachment in ctx.message.attachments:
        if attachment.filename.endswith('.txt'):
            txt_attachment = attachment
        elif attachment.filename.endswith('.jpg'):
            image_attachment = attachment

    if txt_attachment is None or image_attachment is None:
        await ctx.send(
            "😢 Dodane przez Ciebie pliki mają zły format. Dodaj obraz (format .jpg) oraz tekst (format .txt).")
        return

    await txt_attachment.save(txt_like_object)
    txt_like_object.seek(0)

    await image_attachment.save(image_like_object)
    image_like_object.seek(0)

    headers = await check_login_and_get_headers(ctx, cache)
    if headers is None:
        return

    full_url = urljoin(URL, f"material/?client={client}&position={position}")

    try:
        response_token = requests.post(
            full_url,
            files={
                'image': ('5.jpg', image_like_object.read(), 'image/jpeg'),
                'text_content': ('5.txt', txt_like_object.read(), 'text/plain')
            },
            headers=headers
)

        response_token.raise_for_status()
    except requests.HTTPError as e:
        raise ValueError(f"Invalid credentials, HTTP status code: {e.response.status_code}")

    response_dict = json.loads(response_token.content)

    await ctx.send(f"Nowy materiał o id {response_dict['id']} dodany do bazy. :+1:")


@bot.command()
async def updateMaterial(ctx, id, client, position):
    if len(ctx.message.attachments) != 2:
        await ctx.send("😢 Dodaj dokładnie dwa pliki: jeden obraz (format .jpg) oraz jeden tekst (format .txt).")
        return

    txt_like_object = io.BytesIO()
    image_like_object = io.BytesIO()

    txt_attachment = None
    image_attachment = None

    for attachment in ctx.message.attachments:
        if attachment.filename.endswith('.txt'):
            txt_attachment = attachment
        elif attachment.filename.endswith('.jpg'):
            image_attachment = attachment

    if txt_attachment is None or image_attachment is None:
        await ctx.send(
            "😢 Dodane przez Ciebie pliki mają zły format. Dodaj obraz (format .jpg) oraz tekst (format .txt).")
        return

    await txt_attachment.save(txt_like_object)
    txt_like_object.seek(0)

    await image_attachment.save(image_like_object)
    image_like_object.seek(0)

    headers = await check_login_and_get_headers(ctx, cache)
    if headers is None:
        return

    full_url = urljoin(URL, f"material/{id}?client={client}&position={position}")

    try:
        response_token = requests.put(
            full_url,
            files={
                'image': ('5.jpg', image_like_object.read(), 'image/jpeg'),
                'text_content': ('5.txt', txt_like_object.read(), 'text/plain')
            },
            headers=headers
        )

        response_token.raise_for_status()
    except requests.HTTPError as e:
        raise ValueError(f"Invalid credentials, HTTP status code: {e.response.status_code}")

    response_dict = json.loads(response_token.content)

    await ctx.send(f"Materiał o id {response_dict['id']} został zaktualizowany. :+1:")


@bot.command()
async def deleteMaterial(ctx, id):
    headers = await check_login_and_get_headers(ctx, cache)
    if headers is None:
        return

    full_url = urljoin(URL, f"material/delete/{id}")

    try:
        response_token = requests.delete(
            full_url,
            headers=headers
        )

        response_token.raise_for_status()
    except requests.HTTPError as e:
        raise ValueError(f"Invalid credentials, HTTP status code: {e.response.status_code}")

    response_dict = json.loads(response_token.content)

    await ctx.send(f"Materiał o id {response_dict['id']} został usunięty. :+1:")

bot.run(TOKEN)
