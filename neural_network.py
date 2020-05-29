""" IMPORTS """

import pandas as pd
import numpy as np

from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense

# load in the data
spotify = pd.read_csv('https://raw.githubusercontent.com/Build-Week-Spotify/ds/master/data/tracks_over_40popularity.csv')
print(spotify.head())


def normalize(vectors):
    return vectors / np.linalg.norm(vectors, axis=1, keepdims=True)


def predict(model, input_vector):
    return model.predict(input_vector).argsort()


def build_model(weights):
    model = Sequential([
        # Dot product between feature vector and reference vectors
        Dense(input_shape=(weights.shape[1],),
              units=weights.shape[0],
              activation='linear',
              name='dense_1',
              use_bias=False)
    ])
    model.set_weights([weights.T])
    return model


def get_results(input_vector, features, best_match=True, amount=5):
    """
    get_results(input_vector, features, best_match=True, amount=5)

    input_vector: audio features of the song to suggest similar songs to,
    plus track_id

    features: full database to suggest songs from
    best_match=True: True if you want most similar songs, False if least
    similar

    amount=5: amount of results to return.

    returns a list (might be a numpy array?) of indices from the original
    database
    """

    col_names = ['acousticness', 'danceability', 'energy', 'instrumentalness',
                 'key', 'liveness',	'loudness',	'speechiness', 'tempo',
                 'valence', 'id']
    input_vector_df = pd.DataFrame([input_vector], columns=col_names)

    cols_to_drop = ['Unnamed: 0', 'artists', 'duration_ms', 'explicit', 'id',
                    'mode', 'name', 'popularity', 'release_date', 'year']
    
    tr_id = input_vector_df['id'].values[0]
    ids = features['id']
    input_vec = input_vector_df.drop(columns=['id'])
    feats = features.drop(columns=cols_to_drop)
    # norm_vector = normalize(input_vec.values)
    norm_vector = normalize(input_vec)
    norm_features = normalize(feats)
    model = build_model(norm_features)
    prediction = np.array(predict(model, norm_vector).argsort())
    prediction = prediction.reshape(prediction.shape[1])
    feats['id'] = ids

    if best_match:
        if tr_id in ids[prediction[-amount:]]:
            return feats.loc[prediction[-amount-1:-1]]
        return feats.loc[prediction[-amount:]]
    return feats.loc[prediction[:amount]]

    
test_audio_features = [0.5,	0.7, 0.7, 0.0, 3, 0.1, -3, 0.03, 130, 0.9,
                       '6oXghnUUe9u2iIZPNfCxjl']   

results_1 = get_results(spotify.iloc[0], spotify, amount=5)
print('-------------------------')
print(results_1)

results_2 = get_results(test_audio_features, spotify, amount=10)
print('-------------------------')
print(results_2)
