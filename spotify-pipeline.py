# Programmer: Colin Joss
# Last date updated: 2-25-2021
# Description: An ETL of my recently played Spotify songs to a simple Sqlite database.

import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas
import datetime
import sqlalchemy
import sqlite3
from pytz import timezone
import secrets


DATABASE_LOCATION = "sqlite:///played_tracks.sqlite"


def milliseconds_to_hms(ms):
    """Converts an int of milliseconds to a string in hours : minutes: seconds form."""
    s, ms = divmod(ms, 1000)
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)

    # Adds zero padding if number is less than 10
    if h < 10:
        h = str(h).zfill(2)
    if m < 10:
        m = str(m).zfill(2)
    if s < 10:
        s = str(s).zfill(2)

    return f"{h}:{m}:{s}"


def convert_timestamp_to_pfc(ts):
    """Transforms timestamp from Stockholm time to Seattle time."""
    stockholm = timezone("Europe/Stockholm")
    seattle = timezone("US/Pacific")

    ts = ts[0:10] + " " + ts[11:19]
    ts_dt_obj = datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")

    ts_localized = stockholm.localize(ts_dt_obj)
    return ts_localized.astimezone(seattle)


if __name__ == "__main__":

    # EXTRACT ------------------------------------------------

    # Authorize access to my Spotify account
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=secrets.client_id,
        client_secret=secrets.client_secret,
        redirect_uri="https://www.google.com/",
        scope="user-read-recently-played"))

    # Set up lists to store data
    song_names = []
    album_names = []
    artist_names = []
    duration = []
    timestamps = []

    # Request access for recently played songs
    results = sp.current_user_recently_played(limit=50)

    # Add data to the appropriate list
    for song in results["items"]:
        song_names.append(song["track"]["name"])
        album_names.append(song["track"]["album"]["name"])
        artist_names.append(song["track"]["album"]["artists"][0]["name"])
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

    # Remove rows with songs that weren't played yesterday:
    index = 0
    today = datetime.datetime.now()
    yesterday = today - datetime.timedelta(days=1)
    for timestamp in song_df["timestamps"]:
        if str(timestamp)[0:10] != str(yesterday)[0:10]:
            song_df = song_df.drop([index])
        index += 1

    # Convert song lengths to h:m:s strings
    song_df["duration"] = song_df["duration"].apply(milliseconds_to_hms)

    # LOAD ------------------------------------------------

    print("Testing 1 2 3")
    # Connects to a database
    engine = sqlalchemy.create_engine(DATABASE_LOCATION)
    connection = sqlite3.connect("played_tracks.sqlite")
    cursor = connection.cursor()

    # Creates database headers if the database does not exist
    sql_query = """
    CREATE TABLE IF NOT EXISTS played_tracks (
        song_name VARCHAR(200),
        album_name VARCHAR(200),
        artist_name VARCHAR(200),
        duration VARCHAR(200),
        timestamps VARCHAR(200)
    )
    """

    cursor.execute(sql_query)
    print("Opened database successfully!")

    # Loads new spotify data into the database!
    song_df.to_sql("played_tracks", engine, index=False, if_exists="append")

    connection.close()
    print("Connection successfully closed.")
