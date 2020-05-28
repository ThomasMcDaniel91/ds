from flask import Blueprint, jsonify
from flask_api.services.spotify_service import spotify_api
from flask_api.services.chart_service import visualize_audio_similarities
from dotenv import load_dotenv
import os
import psycopg2
import pandas as pd
from joblib import load

spotify_routes = Blueprint("spotify_routes", __name__)

load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PW = os.getenv("DB_PW")
DB_HOST = os.getenv("DB_HOST")

username = os.getenv("CHART_USERNAME")
api_key = os.getenv("CHART_API_KEY")

@spotify_routes.route("/")
def index(): #test our DB connection and verify we can pull data out in json format.
    pg_conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER,
        password=DB_PW, host=DB_HOST
    )
    pg_curs = pg_conn.cursor()

    query = '''SELECT * FROM tracks LIMIT 5'''

    pg_curs.execute(query)
    result = pg_curs.fetchall()

    pg_curs.close()
    pg_conn.close()
    return jsonify(result)

@spotify_routes.route("/dummy_data")
def dummy_data(): #just some dummy data to get working with.
  dummy_list = [
            {'title': 'The Ocean - 1990 Remaster',
            'album_name': 'Houses of the Holy (1994 Remaster)',
            'artist': 'Led Zeppelin',
            'album_art': 'https://i.scdn.co/image/ab67616d0000b273441fd03f69579d36801631d9'
            },
            
            {'title': 'I Disappear',
            'album_name': 'I Disappear',
            'artist': 'Metallica',
            'album_art': 'https://i.scdn.co/image/ab67616d0000b273bfe41664b2ca1038b5e3bc6c'
            },

            {'title': 'Creeping Death (Remastered)',
            'album_name': 'Ride The Lightning (Deluxe Remaster)',
            'artist': 'Metallica',
            'album_art': 'https://i.scdn.co/image/ab67616d0000b273533fd0b248052d04e6b732c0'
            },

            {'title': "I Guess That's Why They Call It The Blues",
            'album_name': 'Too Low For Zero',
            'artist': 'Elton John',
            'album_art': 'https://i.scdn.co/image/ab67616d0000b273eb11e2abccdca41f39ad3b89'
            },

            {'title': 'Sweet Leaf - 2014 Remaster',
            'album_name': 'Master of Reality (2014 Remaster)',
            'artist': 'Black Sabbath',
            'album_art': 'https://i.scdn.co/image/ab67616d0000b273c199494ba9ea2b73e9208f91'
            }
  ]
  return jsonify(dummy_list)


@spotify_routes.route("/search/<artist_name>/<track_name>", methods=['GET', 'POST'])
def recommendations(artist_name, track_name):
    pg_conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER,
        password=DB_PW, host=DB_HOST
    )
    pg_curs = pg_conn.cursor()
    
    sp = spotify_api()
    
    result = sp.search(q=f'artist: {artist_name} track: {track_name}')
    result = result['tracks']['items']

    track_id = result[0]['id']
    track_name = result[0]['name']
    artist_name = result[0]['artists'][0]['name']

    features = sp.audio_features(track_id)
    features = features[0]

    ##reorder the features to match expected input for the model
    features = {'acousticness': features["acousticness"], 'danceability': features["danceability"],
                'energy': features['energy'], 'instrumentalness': features['instrumentalness'], 'key': features['key'],
                'liveness': features['liveness'], 'loudness': features['loudness'],
                'speechiness': features['speechiness'],
                'tempo': features['tempo'], 'valence': features['valence']}

    features_df = pd.DataFrame(features, index=[0])

    scaler = load('scaler.joblib')
    audio_feats_scaled = scaler.transform(features_df)

    model = load('test_model.joblib')
    prediction = model.kneighbors(audio_feats_scaled)

    similar_songs_index = prediction[1][0][:].tolist()

    recommendations_list = []
    artist_list = []
    title_list = []
    similar_song_ids = []
    similar_songs_features = []

    for i, value in enumerate(similar_songs_index):
        query = f'''SELECT * FROM tracks WHERE index={value}'''
        pg_curs.execute(query)
        result = pg_curs.fetchall()

        list_of_feats = [result[0][1], result[0][3], result[0][5], result[0][8], result[0][9], result[0][10], # retrieve audio features from the fetched query
                         result[0][11], result[0][16], result[0][17], result[0][18]]
        similar_songs_features.append(list_of_feats)

        song_id = result[0][7]

        artist = result[0][2]
        title = result[0][13]

        if i != 0:  # don't run on first iteration
            if title in title_list:
                if artist in artist_list:  # if both title and artist already exist as a prediction, this is a duplicate, lets skip it.
                    continue
        if artist == f"['{artist_name}']" and title == track_name:
            continue

        artist_list.append(result[0][2])
        title_list.append(result[0][13])

        # For Kyle's chart function.
        similar_song_ids.append(song_id)
        similar_song_ids.append(title)
        similar_song_ids.append(artist)

        spotify_result = sp.search(q=f'artist: {artist} track: {title}')

        album_name = spotify_result['tracks']['items'][0]['album']['name']
        album_result = spotify_result['tracks']['items'][0]['album']['images'][0]['url']

        recommendations_list.append({"title": title, "album_name": album_name, "artist": artist,
                                     "album_art": album_result, "song_id": song_id})

        if len(recommendations_list) > 4:
            break

    column_names = features_df.columns.tolist() # retrieve column names and ordering from manually defined near the start of the route

    audio_feats_scaled_df = pd.DataFrame(audio_feats_scaled, columns=column_names)

    similar_feats_scaled = scaler.transform(similar_songs_features)
    similar_feats_scaled_df = pd.DataFrame(similar_feats_scaled, columns=column_names)

    similar_feats_averaged = []

    for col in column_names:
        avg = similar_feats_scaled_df[col].mean()
        similar_feats_averaged.append(avg)

    similar_feats_averaged_df = pd.DataFrame([similar_feats_averaged], columns=column_names)

    visual_df = pd.concat([audio_feats_scaled_df, similar_feats_averaged_df, similar_feats_scaled_df],
                          ignore_index=False)

    iframe = visualize_audio_similarities(visual_df, username, api_key, similar_song_ids)

    recommendations_list.append({"iframe": iframe})

    pg_curs.close()
    pg_conn.close()

    return jsonify(recommendations_list)


# @spotify_routes.route("/test_search/<artist_name>/<track_name>", methods=['GET', 'POST'])
# def test_recommendations(artist_name, track_name):
#     pg_conn = psycopg2.connect(
#         dbname=DB_NAME, user=DB_USER,
#         password=DB_PW, host=DB_HOST
#     )
#     pg_curs = pg_conn.cursor()
#
#     sp = spotify_api()
#
#     result = sp.search(q=f'artist: {artist_name} track: {track_name}')
#     result = result['tracks']['items']
#
#     track_id = result[0]['id']
#     track_name = result[0]['name']
#     artist_name = result[0]['artists'][0]['name']
#
#     features = sp.audio_features(track_id)
#     features = features[0]
#
#     ##reorder the features to match expected input for the model
#     features = {'acousticness': features["acousticness"], 'danceability': features["danceability"],
#                 'energy': features['energy'], 'instrumentalness': features['instrumentalness'], 'key': features['key'],
#                 'liveness': features['liveness'], 'loudness': features['loudness'],
#                 'speechiness': features['speechiness'],
#                 'tempo': features['tempo'], 'valence': features['valence']}
#
#     features_df = pd.DataFrame(features, index=[0])
#
#     scaler = load('scaler.joblib')
#     audio_feats_scaled = scaler.transform(features_df)
#
#     model = load('test_model.joblib')
#     prediction = model.kneighbors(audio_feats_scaled)
#
#     similar_songs_index = prediction[1][0][:].tolist()
#
#     recommendations_list = []
#     artist_list = []
#     title_list = []
#     similar_song_ids = []
#     similar_songs_features = []
#
#     for i, value in enumerate(similar_songs_index):
#         query = f'''SELECT * FROM tracks WHERE index={value}'''
#         pg_curs.execute(query)
#         result = pg_curs.fetchall()
#
#         list_of_feats = [result[0][1], result[0][3], result[0][5], result[0][8], result[0][9], result[0][10],
#                          # retrieve audio features from the fetched query
#                          result[0][11], result[0][16], result[0][17], result[0][18]]
#         similar_songs_features.append(list_of_feats)
#
#         song_id = result[0][7]
#
#         artist = result[0][2]
#         title = result[0][13]
#
#         if i != 0:  # don't run on first iteration
#             if title in title_list:
#                 if artist in artist_list:  # if both title and artist already exist as a prediction, this is a duplicate, lets skip it.
#                     continue
#         if artist == f"['{artist_name}']" and title == track_name:
#             continue
#
#         artist_list.append(result[0][2])
#         title_list.append(result[0][13])
#
#         # For Kyle's chart function.
#         similar_song_ids.append(song_id)
#         similar_song_ids.append(title)
#         similar_song_ids.append(artist)
#
#         spotify_result = sp.search(q=f'artist: {artist} track: {title}')
#
#         album_name = spotify_result['tracks']['items'][0]['album']['name']
#         album_result = spotify_result['tracks']['items'][0]['album']['images'][0]['url']
#
#         recommendations_list.append({"title": title, "album_name": album_name, "artist": artist,
#                                      "album_art": album_result, "song_id": song_id})
#
#         if len(recommendations_list) > 4:
#             break
#
#     column_names = features_df.columns.tolist()  # retrieve column names and ordering from manually defined near the start of the route
#
#     audio_feats_scaled_df = pd.DataFrame(audio_feats_scaled, columns=column_names)
#
#     similar_feats_scaled = scaler.transform(similar_songs_features)
#     similar_feats_scaled_df = pd.DataFrame(similar_feats_scaled, columns=column_names)
#
#     similar_feats_averaged = []
#
#     for col in column_names:
#         avg = similar_feats_scaled_df[col].mean()
#         similar_feats_averaged.append(avg)
#
#     similar_feats_averaged_df = pd.DataFrame([similar_feats_averaged], columns=column_names)
#
#     visual_df = pd.concat([audio_feats_scaled_df, similar_feats_averaged_df, similar_feats_scaled_df],
#                           ignore_index=False)
#
#     print(username, api_key)
#
#     iframe = visualize_audio_similarities(visual_df, username, api_key, similar_song_ids)
#
#     recommendations_list.append({"iframe": iframe})
#
#     pg_curs.close()
#     pg_conn.close()
#
#     return jsonify(recommendations_list)