import json
from io import StringIO, BytesIO
from PIL import Image
from typing import Union
from google.cloud import storage
from discord import File
from google.oauth2.service_account import Credentials
import io

# -------------------
# File Handling Utils
# -------------------

def get_from_gcp_storage(file_name: str, bucket_name: str):
    """Download a file from Google Cloud Storage."""
    with open("iam-storage.json") as f:
        json_content = json.load(f)

    credentials = Credentials.from_service_account_info(json_content)

    storage_client = storage.Client(credentials=credentials)

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    content = blob.download_as_bytes()

    return content


def get_image(image: Union[str, bytes]) -> Image:
    """Convert an image to a Discord File object."""
    image_obj = None
    if isinstance(image, str):
        image_obj = Image.open(image)
    elif isinstance(image, bytes):
        image_obj = Image.open(BytesIO(image))
    else:
        raise TypeError(f"image must be str or bytes - it's {type(image)}")

    if image_obj:
        image_binary = BytesIO()
        image_obj.save(image_binary, 'PNG')
        image_binary.seek(0)
        return File(fp=image_binary, filename="image.png")


def get_txt(content: Union[bytes, str]) -> str:
    """Convert a text content to a string."""

    if isinstance(content, bytes):
        content = content.decode("utf-8")
    elif not isinstance(content, str):
        raise TypeError("content must be bytes or str")

    file = StringIO(content)

    return file.read()


async def handle_image_and_text_attachments(ctx, attachments):
    """Handle image and text attachments in Discord commands."""
    if len(attachments) != 2:
        await ctx.send("😢 Dodaj dokładnie dwa pliki: jeden obraz (format .jpg) oraz jeden tekst (format .txt).")
        return None, None

    txt_like_object = io.BytesIO()
    image_like_object = io.BytesIO()

    txt_attachment = None
    image_attachment = None

    for attachment in attachments:
        if attachment.filename.endswith('.txt'):
            txt_attachment = attachment
        elif attachment.filename.endswith('.jpg'):
            image_attachment = attachment

    if txt_attachment is None or image_attachment is None:
        await ctx.send("😢 Dodane przez Ciebie pliki mają zły format. Dodaj obraz (format .jpg) oraz tekst (format .txt).")
        return None, None

    await txt_attachment.save(txt_like_object)
    txt_like_object.seek(0)

    await image_attachment.save(image_like_object)
    image_like_object.seek(0)

    return txt_like_object, image_like_object


async def handle_csv_attachment(ctx, attachments):
    if len(attachments) != 1:
        await ctx.send("😢 Dodaj dokładnie jeden plik: lista grup (format .csv).")
        return None

    csv_like_object = io.BytesIO()

    csv_attachment = None
    for att in attachments:
        if att.filename.endswith('.csv'):
            csv_attachment = att
            break

    if csv_attachment is None:
        await ctx.send("😢 Dodane przez Ciebie plik ma zły format. Dodaj plik w formacie .csv.")
        return None

    await csv_attachment.save(csv_like_object)
    csv_like_object.seek(0)

    return csv_like_object

