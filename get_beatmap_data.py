#!/usr/bin/env python

"""
get_beatmap_data.py: Gets a list of valid beatmap_ids using osu api, and stores it in beatmap_data.json
"""

import json
import requests
from requests.structures import CaseInsensitiveDict

beatmap_ids = []
beatmap_data = {}  # key = id, value = data
access_token = ""


def load_beatmap_ids():
    global beatmap_ids
    with open('beatmap_ids.json', 'r', encoding='utf-16') as f:
        beatmap_ids = json.loads(f.read())


def load_beatmap_data():
    global beatmap_data
    with open('beatmap_data.json', 'r', encoding='utf-16') as f:
        beatmap_data = json.loads(f.read())


def save_beatmap_data():
    with open('beatmap_data.json', 'w', encoding='utf-16') as f:
        f.write(json.dumps(beatmap_data))


def get_beatmap_data(beatmap_id):
    """
    This function returns a dict containing beatmap data from the beatmap with id beatmap_id
    """
    while True:
        try:
            url = "https://osu.ppy.sh/api/v2/beatmaps/lookup?id=" + str(beatmap_id)
            headers = CaseInsensitiveDict()
            headers["Content-Type"] = "application/json"
            headers["Accept"] = "application/json"
            headers["Authorization"] = "Bearer " + access_token
            headers["mode"] = "osu!standard"

            response = requests.get(url, headers=headers, timeout=(3, 3))
            response.raise_for_status()
            return response.json()
        except requests.exceptions as e:
            print(e)


def id_data_to_file():
    global access_token
    with open("access_token.txt", "r", encoding="utf-16") as f:
        access_token = f.read()
        
    load_beatmap_ids()
    #load_beatmap_data()
    print(beatmap_ids)
    
    for idx, beatmap_id in enumerate(beatmap_ids):
        if idx % 10 == 0:
            print(str(idx) + "/" + str(len(beatmap_ids)))
            save_beatmap_data()
        
        if beatmap_id not in beatmap_data:
            try:
                beatmap_data[beatmap_id] = get_beatmap_data(beatmap_id)
            except requests.exceptions.HTTPError:
                pass
    
    save_beatmap_data()
    


id_data_to_file()
