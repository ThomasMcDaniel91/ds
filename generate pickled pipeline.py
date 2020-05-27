""" IMPORTS """

import pandas as pd

from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors


def load_and_clean():
    """
    spotify, identify = load_and_clean()
    """
    spotify = pd.read_csv(
        'https://raw.githubusercontent.com/Build-Week-Spotify/ds/master/data/tracks_over_40popularity.csv')

    # dataframe that serves to identify songs
    identify = spotify[['artists', 'id', 'name']]

    # dataframe consisting of audio features we want to train on
    spotify = spotify.drop(columns=['Unnamed: 0',
                                    'artists',
                                    'duration_ms',
                                    'explicit',
                                    'id',
                                    'mode',
                                    'name',
                                    'popularity',
                                    'release_date',
                                    'year'])

    return spotify, identify


spotify, identify = load_and_clean()
print(spotify.shape)
print(spotify.head())
print('-----------------')
print(identify.shape)
print(identify.head())


def knn_predictor(audio_feats):
    """
    similar_song_ids, visual_df = knn_predictor(audio_features)
    """
    # from sklearn.pipeline import Pipeline
    from joblib import dump

    # Scale the data with standard scaler

    # pipeline = Pipeline([('encoder', StandardScaler()),
    #                     ('model', NearestNeighbors(n_neighbors=6, algorithm='kd_tree'))])
    #
    # pipeline.fit(spotify)
    # dump(pipeline, 'test_model.joblib', compress=True)

    scaler = StandardScaler()
    spotify_scaled = scaler.fit_transform(spotify)

    dump(scaler, 'scaler.joblib', compress=True)

    ################################################
    audio_feats_scaled = scaler.transform([audio_feats])

    ## Nearest Neighbors model
    nn = NearestNeighbors(n_neighbors=21, algorithm='kd_tree')
    nn.fit(spotify_scaled)

    dump(nn, 'test_model.joblib', compress=True)

    # prediction
    prediction = nn.kneighbors(audio_feats_scaled)

    # Get the indexes of the list of similar songs
    similar_songs_index = prediction[1][0][1:].tolist()

    # Create an empty list to store simlar song names
    similar_song_ids = []

    # loop over the indexes and append song names to empty list above
    for i in similar_songs_index:
        print("Song index: ", i)
        song_id = identify['id'].iloc[i]
        similar_song_ids.append(song_id)

    #################################################

    column_names = spotify.columns.tolist()

    # put scaled audio features into a dataframe
    audio_feats_scaled_df = pd.DataFrame(audio_feats_scaled, columns=column_names)

    # create empty list of similar songs' features
    similar_songs_features = []

    # loop through the indexes of similar songs to get audio features for each
    # . similar song
    for index in similar_songs_index:
        list_of_feats = spotify.iloc[index].tolist()
        similar_songs_features.append(list_of_feats)

    # scale the features and turn them into a dataframe
    similar_feats_scaled = scaler.transform(similar_songs_features)
    similar_feats_scaled_df = pd.DataFrame(similar_feats_scaled, columns=column_names)

    # create empty list for averaged features of recommended songs
    similar_feats_averaged = []

    # loop through columns of audio features and get average of each column for 5
    # . recommended songs
    for col in column_names:
        avg = similar_feats_scaled_df[col].mean()
        similar_feats_averaged.append(avg)

    # turn averages into 1 row dataframe
    similar_feats_averaged_df = pd.DataFrame([similar_feats_averaged], columns=column_names)

    # concatenate this with input songs audio features to be used for visualizing
    visual_df = pd.concat([audio_feats_scaled_df, similar_feats_averaged_df], ignore_index=True)

    return similar_song_ids, visual_df


# test_audio_features = [0.5, 0.7, 0.7, 0.0, 3, 0.1, -3, 0.03, 130, 0.9]
test_audio_features = [0.0797, 0.654, 0.76, 0, 0, 0.299, -3.669, 0.045, 99.945, 0.41]
similar_song_ids, visual_df = knn_predictor(test_audio_features)

print('-----------------')
print('Recommended song_ids:')
print(similar_song_ids)
print('-----------------')
print(visual_df)
print(identify.head())