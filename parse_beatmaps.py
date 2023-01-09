import json
import requests
from requests.structures import CaseInsensitiveDict

beatmaps = {}  # key = id, value = dict of stats
valid_ids = []


def get_beatmap_data(beatmap_id):
    """
    This function returns a dict containing beatmap data from the beatmap with id
    """
    url = "https://osu.ppy.sh/api/v2/beatmaps/lookup?id=" + str(beatmap_id)
    with open("access_token.txt", "r", encoding="utf-16") as f:
        access_token = f.read()
    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"
    headers["Accept"] = "application/json"
    headers["Authorization"] = "Bearer " + access_token
    headers["mode"] = "osu!standard"

    response = requests.get(url, headers=headers, timeout=(1, 1))
    response.raise_for_status()
    return response.json()


def save_to_dict():
    """
    Gets data about beatmap and saves it into json file
    """
    global beatmaps
    with open('beatmap_data.json', 'r', encoding='utf-16') as f:
        beatmaps = json.loads(f.read())
    load_ids()

    counter = 0
    for valid_id in valid_ids:
        if counter % 50 == 0:
            print(str(counter) + "/" + str(len(valid_ids)))
            save_to_file(beatmaps, 'beatmap_data.json')

        if str(valid_id) not in beatmaps:
            try:
                beatmap_dict = get_beatmap_data(valid_id)
                beatmaps[valid_id] = beatmap_dict

            except requests.exceptions.ReadTimeout:
                pass

        counter += 1
    save_to_file(beatmaps, 'beatmap_data.json')


def load_ids():
    """
    Reads ids from csv file into list beatmap_ids
    """
    global valid_ids
    with open('beatmap_ids.json', 'r', encoding="utf-16") as f:
        valid_ids = json.loads(f.read())


def save_to_file(dict, filename):
    with open(filename, 'w', encoding='utf-16') as f:
        f.write(json.dumps(dict))


save_to_dict()
