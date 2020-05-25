import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

client_id = "733b06048d3b42fb8ef442596c6f3ff3"
client_secret = "01513b28eef64193b2ffac417e6b7ebb"

def spotify_api():
    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    return sp