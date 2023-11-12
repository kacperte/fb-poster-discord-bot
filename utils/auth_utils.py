import requests
import json
from urllib.parse import urljoin

# -------------------
# Authentication Utils
# -------------------


def get_credentials(URL, login, password):
    """Authenticate the user and get the authorization headers."""
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


async def check_login_and_get_headers(ctx, cache):
    """Check if the user is logged in and return the authorization headers."""
    user = ctx.author
    if user not in cache:
        await ctx.send("😢 Nie jesteś zalogowany. Użyj komendy `setLogin` aby się zalogować.")
        return None
    return cache[user]['grant']


async def make_api_request(ctx, url, headers=None, method='GET', **kwargs):
    """Make an API request and return the JSON response."""
    try:
        response = requests.request(method, url, headers=headers, **kwargs)

        response.raise_for_status()
        return json.loads(response.content)
    except requests.HTTPError as e:
        await ctx.send(response.content)
        raise ValueError(f"Invalid credentials, HTTP status code: {e.response.status_code}")
