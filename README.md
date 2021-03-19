# spotify-pipeline

spotify-pipeline is a program accesses my recently played
songs from my Spotify account and stores it in a 
Sqlite database. On my personal laptop, I exported this
script as a .exe and scheduled Windows to run it once a day.

I partially followed the structure laid out in YouTuber
Karolina Sowinska's three-part data engineering tutorial to
make this program. I also waded through Spotify's API 
tutorials.

## Technologies

Project made with:
- spotipy 2.16.1
- pandas 1.2.2
- datetime
- sqlalchemy
- sqlite3
- pytz 2021.1

## Installation

Clone from Github and run in the terminal.