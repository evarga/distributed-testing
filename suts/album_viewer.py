import requests


def get_access_token(client_id, client_secret, base_addr="https://accounts.spotify.com"):
    """
    Retrieves a Spotify access token using the client credentials flow.
    See https://developer.spotify.com/documentation/web-api/tutorials/client-credentials-flow

    :param client_id: Spotify client ID.
    :param client_secret: Spotify client secret.
    :param base_addr: Spotify's API base address for getting access token.
    :returns: Spotify access token.
    :raises Exception: If the request to retrieve the access token fails.
    """
    response = requests.post(
        base_addr + "/api/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret
        }
    )
    if response.status_code != 200:
        raise Exception("Failed to get access token: {}".format(response.text))
    return response.json()["access_token"]


def get_artist(artist_name, access_token, base_addr="https://api.spotify.com"):
    """
    Retrieves the first artist ID from the Spotify API.
    See https://developer.spotify.com/documentation/web-api/reference/search

    :param artist_name: Spotify artist name.
    :param access_token: Spotify access token.
    :param base_addr: Spotify's API base address for getting artist information.
    :returns: Artist identifier.
    :raises Exception: If the request to retrieve the artist information fails.
    """
    response = requests.get(
        base_addr + "/v1/search",
        headers={"Content-Type": "application/json",
                 "Authorization": "Bearer {}".format(access_token)},
        params={"q": artist_name,
                "type": "artist",
                "limit": 1}
    )
    if response.status_code != 200:
        raise Exception("Failed to get artist: {}".format(response.text))
    return response.json()["artists"]["items"][0]["id"]


def get_albums(artist_id, access_token, base_addr="https://api.spotify.com"):
    """
    Retrieves albums from the Spotify API.
    See https://developer.spotify.com/documentation/web-api/reference/artists/get-artists-albums

    :param artist_id: Spotify artist identifier.
    :param access_token: Spotify access token.
    :param base_addr: Spotify's API base address for getting album information.
    :returns: List of albums.
    :raises Exception: If the request to retrieve the album information fails.
    """
    response = requests.get(
        "{}/{}/albums".format(base_addr + "/v1/artists", artist_id),
        headers={"Content-Type": "application/json",
                 "Authorization": "Bearer {}".format(access_token)},
        params={"include_groups": "album",
                "market": "US",
                "limit": 50}
    )
    if response.status_code != 200:
        raise Exception("Failed to get albums: {}".format(response.text))
    return response.json()["items"]
