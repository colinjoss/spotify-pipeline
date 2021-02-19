# Programmer: Colin Joss
# Last date updated: 2-17-2021
# Description:


# import requests
# response = requests.get("https://api.spotify.com")
# spotify = response.json()
# print(spotify)

import sqlalchemy
import pandas
from sqlalchemy.orm import sessionmaker
import requests
import json
import datetime
import sqlite3
import base64

DATABASE_LOCATION = "sqlite:///my_played_tracks.sqlite"
USER_ID = "12129815625"
TOKEN = "BQBK0Y7Lo5Ge-tJ1Sz75ieTxVFkNhXEI8T5OGP5uKqsw23KPIUa9mC70vNhc3jQrlbADx08CWJPCgN2Tvyc139xR5gb9ENALlqo7XHLBzeE_cI8PXvBpylZZHnqG2a-NZfAZ7zL1m5b9agh1uUrLMw"

if __name__ == "__main__":

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TOKEN}"
    }

    today = datetime.datetime.now()
    yesterday = today - datetime.timedelta(days=1)
    yesterday_unix_timestamp = int(yesterday.timestamp()) * 1000
    now_unix_timestamp = int(today.timestamp()) * 1000

    response = requests.get(f"https://api.spotify.com/v1/me/player/recently-played?limit=50&before={now_unix_timestamp}",
                            headers=headers).json()
    print(response)

    song_names = []
    artist_names = []
    played_at_list = []
    timestamps = []

    for song in response["items"]:
        song_names.append(song["track"]["name"])
        artist_names.append(song["track"]["album"]["artists"][0]["name"])
        played_at_list.append(song["played_at"])
        timestamps.append(song["played_at"][0:10])

    song_dict = {
        "song_name": song_names,
        "artist_name": artist_names,
        "played_at": played_at_list,
        "timestamps": timestamps
    }

    song_df = pandas.DataFrame(song_dict, columns=["song_name", "artist_name", "played_at", "timestamps"])

    print(song_df)
