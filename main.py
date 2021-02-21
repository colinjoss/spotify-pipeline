# Programmer: Colin Joss
# Last date updated: 2-17-2021
# Description:

import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id="7406bc4c83534c57bdc0cf3e8b6991d5",
    client_secret="6d5fa9a24d444ef89793c953aa88d87a",
    redirect_uri="https://www.google.com/",
    scope="user-read-recently-played"))

song_names = []
artist_names = []
played_at_list = []
timestamps = []

results = sp.current_user_recently_played(limit=50)
for song in results["items"]:
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
