# Programmer: Colin Joss
# Last date updated: 2-22-2021
# Description:

import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas
import csv
import datetime
import pytz
from pytz import timezone
# print(pytz.common_timezones)


def milliseconds_to_hms(ms):
    """Converts an int of milliseconds to a string in hours : minutes: seconds form."""
    s, ms = divmod(ms, 1000)
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    return f"{h}:{m}:{s}"


def get_timestamps_from_csv(filename):
    """Collects the timestamps from rows in a preexisting csv into a list."""
    csv_timestamps = []
    with open(f"{filename}", "r") as infile:
        csv_file = csv.reader(infile)
        for row in csv_file:
            csv_timestamps += [row[6]]
    return csv_timestamps


def convert_to_ascii(string):
    """"""
    try:
        string.encode(encoding='utf-8').decode('ascii')
    except UnicodeDecodeError:
        return string.encode('utf-8')
    return string


def convert_timestamp_to_pfc(timestamp):
    stockholm = timezone("Europe/Stockholm")
    seattle = timezone("US/Pacific")

    timestamp = timestamp[0:10] + " " + timestamp[11:19]
    timestamp_dt_obj = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")

    timestamp_localized = stockholm.localize(timestamp_dt_obj)
    return timestamp_localized.astimezone(seattle)


if __name__ == "__main__":

    # EXTRACT ------------------------------------------------

    # Authorize access to my Spotify account
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id="7406bc4c83534c57bdc0cf3e8b6991d5",
        client_secret="6d5fa9a24d444ef89793c953aa88d87a",
        redirect_uri="https://www.google.com/",
        scope="user-read-recently-played"))

    # Set up lists to store data
    song_names = []
    album_names = []
    artist_names = []
    duration = []
    timestamps = []

    # Calculate current timestamp and a timestamp 24 hours ago from now
    today = datetime.datetime.now()
    now_unix_timestamp = int(today.timestamp()) * 1000
    yesterday_unix_timestamp = now_unix_timestamp - 86400

    # Request access for recently played songs within the given time frame
    results = sp.current_user_recently_played(limit=50)

    # Add data to the appropriate list
    for song in results["items"]:
        song_names.append(convert_to_ascii(song["track"]["name"]))
        album_names.append(convert_to_ascii(song["track"]["album"]["name"]))
        artist_names.append(convert_to_ascii(song["track"]["album"]["artists"][0]["name"]))
        duration.append(song["track"]["duration_ms"])
        timestamps.append(song["played_at"])

    # Put acquired data in a data frame
    song_dict = {
        "song_name": song_names,
        "album_name": album_names,
        "artist_name": artist_names,
        "duration": duration,
        "timestamps": timestamps
    }

    song_df = pandas.DataFrame(song_dict, columns=["song_name", "album_name", "artist_name",
                                                   "duration", "timestamps"])

    # TRANSFORM ------------------------------------------------

    # Stop execution if no songs played in the last 24 hours
    if song_df.empty:
        raise Exception("No data retrieved within the past 24 hours. Finishing execution.")

    # Stop execution if there are duplicates in the data
    if song_df["timestamps"].is_unique is False:
        raise Exception("Primary key check violated. Finishing execution.")

    # Stop execution if null values returned
    if song_df.isnull().values.any():
        raise Exception("Null values found. Finishing execution.")

    # Convert timestamps to US/Pacific time
    song_df["timestamps"] = song_df["timestamps"].apply(convert_timestamp_to_pfc)

    # Convert song lengths to h:m:s strings
    song_df["duration"] = song_df["duration"].apply(milliseconds_to_hms)

    # LOAD ------------------------------------------------

    with open("spotify-data.csv", 'a', newline="") as outfile:  # *** LOAD
        song_df.to_csv(outfile, header=False, encoding="utf-8")
