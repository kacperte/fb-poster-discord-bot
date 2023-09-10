import requests
import json
from urllib.parse import urljoin
from io import StringIO, BytesIO
from PIL import Image
from typing import Union
from google.cloud import storage
from discord import File
from google.oauth2.service_account import Credentials


def get_credentials(URL, login, password):
    full_url = urljoin(URL, "token")
    try:
        # Send a request to the token endpoint to authenticate the user
        response_token = requests.post(
            url=full_url,
            data={
                "grant_type": "password",
                "username": login,
                "password": password,
            },
        )
        response_token.raise_for_status()  # Raise an exception if the status code is not in the 200s
    except requests.HTTPError as e:
        # If an error occurs, raise an HTTPException with a 400 status code and an error message
        raise ValueError(f"Invalid credentials, HTTP status code: {e.response.status_code}")

    # Parse the access token from the token response and add it to the headers for subsequent requests
    response_dict = json.loads(response_token.content)
    auth_token = response_dict["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}

    return headers


def get_from_gcp_storage(file_name: str, bucket_name: str):
    with open("iam-storage.json") as f:
        json_content = json.load(f)

    credentials = Credentials.from_service_account_info(json_content)

    storage_client = storage.Client(credentials=credentials)

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    content = blob.download_as_bytes()

    return content


def get_image(image: Union[str, bytes]) -> Image:
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

    if isinstance(content, bytes):
        content = content.decode("utf-8")
    elif not isinstance(content, str):
        raise TypeError("content must be bytes or str")

    file = StringIO(content)

    return file.read()


async def check_login_and_get_headers(ctx, cache):
    user = ctx.author
    if user not in cache:
        await ctx.send("😢 Nie jesteś zalogowany. Użyj komendy `setLogin` aby się zalogować.")
        return None
    return cache[user]['grant']


async def make_api_request(ctx, url, headers, method='GET', **kwargs):
    try:
        response = requests.request(method, url, headers=headers, **kwargs)
        response.raise_for_status()
        return json.loads(response.content)
    except requests.HTTPError as e:
        raise ValueError(f"Invalid credentials, HTTP status code: {e.response.status_code}")


