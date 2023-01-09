#!/usr/bin/env python

"""
get_valid_ids.py: Gets a list of valid beatmap_ids using osu api, and stores it in beatmap_ids.json
"""

import requests
from requests.structures import CaseInsensitiveDict
import json

access_token = ""
beatmap_ids = []


def get_beatmap_leaderboards(beatmap_id):
    """
    Returns a list of user_ids of a beatmaps leaderboards
    """
    while True:
        try:
            url = "https://osu.ppy.sh/api/v2/beatmaps/" + str(beatmap_id) + "/scores"

            headers = CaseInsensitiveDict()
            headers["Content-Type"] = "application/json"
            headers["Accept"] = "application/json"
            headers["Authorization"] = "Bearer " + access_token

            response = requests.get(url, headers=headers, timeout=(3, 3))
            response.raise_for_status()
            scores = response.json()['scores']  # list of score dicts
            user_ids = [score['user_id'] for score in scores]
            return user_ids
        except requests.exceptions as e:
            print(e)


def get_user_recent_plays(user_id):
    """
    Returns a list of beatmap_id from a users most recently played beatmaps
    """
    while True:
        try:
            url = "https://osu.ppy.sh/api/v2/users/" + str(user_id) + "/scores/recent"

            headers = CaseInsensitiveDict()
            headers["Content-Type"] = "application/json"
            headers["Accept"] = "application/json"
            headers["Authorization"] = "Bearer " + access_token
            headers["mode"] = "osu!standard"

            response = requests.get(url, headers=headers, timeout=(3, 3))
            response.raise_for_status()
            recents = response.json()
            recent_ids = [recent['beatmap']['id'] for recent in recents]
            return recent_ids
        except requests.exceptions as e:
            print(e)


def add_ids(quantity_to_add):
    """
    Adds quantity # of unique ids to beatmap_ids.json
    """
    global access_token
    global beatmap_ids

    with open("access_token.txt", "r", encoding="utf-16") as f:
        access_token = f.read()

    beatmap_id_queue = []
    user_id_queue = []

    with open('beatmap_ids.json', 'r', encoding='utf-16') as f:
        beatmap_ids = json.loads(f.read())

    beatmap_id_queue.extend(beatmap_ids[-5:])  # starting point

    count = 0  # start negative because first one doesn't count
    while (count < quantity_to_add):
        if count % 25 == 0:
            print(str(count) + "/" + str(quantity_to_add))
            with open('beatmap_ids.json', 'w', encoding='utf-16') as f:
                f.write(json.dumps(beatmap_ids))

        cur_beatmap_id = beatmap_id_queue.pop()

        if len(user_id_queue) < 1000:
            user_id_queue.extend(get_beatmap_leaderboards(cur_beatmap_id))
        while len(beatmap_id_queue) < 100 and len(user_id_queue) > 0:
            cur_user_id = user_id_queue.pop()
            beatmap_id_queue.extend(get_user_recent_plays(cur_user_id))

        if cur_beatmap_id not in beatmap_ids:
            beatmap_ids.append(cur_beatmap_id)
            count += 1

        if len(user_id_queue) == 0 and len(beatmap_id_queue) == 0:
            break
        
    with open('beatmap_ids.json', 'w', encoding='utf-16') as f:
        f.write(json.dumps(beatmap_ids))


add_ids(2000)
