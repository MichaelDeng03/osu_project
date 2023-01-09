import requests
from requests.structures import CaseInsensitiveDict


def get_access_token(client_id, client_secret):
    """
    Gets access token and saves it to file access_token
    """
    url = "https://osu.ppy.sh/oauth/token"
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Content-Type"] = "application/json"
    data = '{"client_id":' + str(client_id) + ',"client_secret":"' + str(
        client_secret) + '","grant_type":"client_credentials","scope":"public"}'
    data = '{"client_id":19594,"client_secret":"NVkhijB29W0hm1UjdioTlhVuxX312OTLyFpTpmKH","grant_type":"client_credentials","scope":"public"}'

    response = requests.post(url, headers=headers, data=data, timeout=(1, 1))
    response.raise_for_status()

    with open('access_token.txt', 'w', encoding='utf-16') as f:
        f.write(response.json()['access_token'])


get_access_token("19594", "NVkhijB29W0hm1UjdioTlhVuxX312OTLyFpTpmKH")