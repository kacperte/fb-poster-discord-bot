import discord
from discord.ext import commands
from utils import *


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
async def getAllMaterials(ctx):
    headers = await check_login_and_get_headers(ctx, cache)
    if headers is None:
        return

    api_endpoint = urljoin(URL, "material")
    materials = await make_api_request(ctx, api_endpoint, headers)
    if materials is None:
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


@bot.command()
async def getMaterial(ctx, id):
    headers = await check_login_and_get_headers(ctx, cache)
    if headers is None:
        return

    api_endpoint = urljoin(URL, f"material/{id}")

    material = await make_api_request(ctx, api_endpoint, headers)
    if material is None:
        return

    raw_image = get_from_gcp_storage(file_name=material['image_name'], bucket_name='fb-poster-bucket')
    raw_text = get_from_gcp_storage(file_name=material['text_name'], bucket_name='fb-poster-bucket')

    image = get_image(raw_image)
    text = get_txt(raw_text)

    title = f"**Klient**: {material['client']}\n**Projekt**: {material['position']} \n**Autor**: {material['user']['username']}"

    await ctx.send(title, file=image)

    await ctx.send(f"```{text}```")


@bot.command()
async def createMaterial(ctx, client, position):
    txt_like_object, image_like_object = await handle_image_and_text_attachments(ctx, ctx.message.attachments)
    if txt_like_object is None or image_like_object is None:
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


@bot.command()
async def updateMaterial(ctx, id, client, position):
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


@bot.command()
async def deleteMaterial(ctx, id):
    headers = await check_login_and_get_headers(ctx, cache)
    if headers is None:
        return

    api_endpoint = urljoin(URL, f"material/delete/{id}")
    response_dict = await make_api_request(ctx, api_endpoint, headers, method='DELETE')

    if response_dict is not None:
        await ctx.send(f"Materiał o id {response_dict['id']} został usunięty. :+1:")

bot.run(TOKEN)
