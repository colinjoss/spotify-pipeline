# Programmer: Colin Joss
# Last date updated: 2-21-2021
# Description:

import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas
import csv
import datetime


def milliseconds_to_hms(ms):
    """Converts an int of milliseconds to a string in hours : minutes: seconds form."""
    s, ms = divmod(ms, 1000)
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    return f"{h}:{m}:{s}"


def read_csv(filename):
    with open(f"{filename}", "r") as infile:
        csv_file = csv.reader(infile)
        return csv_file


def get_timestamps_from_csv(csv_file):
    csv_timestamps = []
    for row in csv_file:
        csv_timestamps += row[6]
    return csv_timestamps


# func: remove duplicates from data
# func: remove null from data
# func: read_csv
# func: find duplicates in csv
# func:


if __name__ == "__main__":
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id="7406bc4c83534c57bdc0cf3e8b6991d5",
        client_secret="6d5fa9a24d444ef89793c953aa88d87a",
        redirect_uri="https://www.google.com/",
        scope="user-read-recently-played"))

    song_names = []
    album_names = []
    artist_names = []
    duration = []
    played_at_list = []
    timestamps = []

    results = sp.current_user_recently_played(limit=50)

    for song in results["items"]:
        if song is not None or song["track"] is not None:
            song_names.append(song["track"]["name"])
            album_names.append(song["track"]["album"]["name"])
            artist_names.append(song["track"]["album"]["artists"][0]["name"])
            duration.append(song["track"]["duration_ms"])
            played_at_list.append(song["played_at"][0:10])
            timestamps.append(song["played_at"])

    duration = [milliseconds_to_hms(length) for length in duration]

    csv_ts = get_timestamps_from_csv(read_csv("test.csv"))
    i = 0
    for ts in timestamps:
        if ts in csv_ts:
            song_names.remove(song_names[i])
            album_names.remove(album_names[i])
            artist_names.remove(artist_names[i])
            duration.remove(duration[i])
            played_at_list.remove(played_at_list[i])
            timestamps.remove(ts)
        i += 1

    song_dict = {
        "song_name": song_names,
        "album_name": album_names,
        "artist_name": artist_names,
        "duration": duration,
        "played_at": played_at_list,
        "timestamps": timestamps
    }

    song_df = pandas.DataFrame(song_dict, columns=["song_name", "album_name", "artist_name",
                                                   "duration", "played_at", "timestamps"])
    with open("test.csv", 'a', newline="") as outfile:
        song_df.to_csv(outfile, header=False)

    print(song_df)
