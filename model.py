
# DS/model.py

""" IMPORTS """
import pandas as pd

from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors

# store data in a Pandas Dataframe
spotify = pd.read_csv('.\data\SpotifyAudioFeaturesApril2019.csv')
print(spotify.head())

# dataframe that serves to identify songs
identify = spotify[['artist_name', 'track_id', 'track_name']]

# dataframe consisting of audio features we want to train on
spotify = spotify.drop(columns = ['artist_name',
                                  'track_id',
                                  'track_name',
                                  'duration_ms',
                                  'mode',
                                  'time_signature',
                                  'popularity'])

# Scale the data with standard scaler
scaler = StandardScaler()
spotify_scaled = scaler.fit_transform(spotify)


def song_recommender_using_audio_feats(audio_feats):
  """
  Input any audio features and output 5 similar songs
  """
  audio_feats_scaled = scaler.transform([audio_feats])

  ## Nearest Neighbors model
  nn = NearestNeighbors(n_neighbors=6, algorithm='kd_tree')
  nn.fit(spotify_scaled)

  # prediction 
  prediction = nn.kneighbors(audio_feats_scaled)

  simlar_songs_index = prediction[1][0][1:].tolist()
  
  similar_songs = []
  
  for i in simlar_songs_index:
    song = identify['track_name'].iloc[i]
    similar_songs.append(song)

  return similar_songs


# use random features to make sure function works on audio features not in dataset
test_audio_features = [0.5,	0.7, 0.7, 0.0, 3, 0.1, -3, 0.03, 130, 0.9]
print('------------------------')
print(song_recommender_using_audio_feats(test_audio_features))



def dataframe_for_visualizations(audio_feats):
  """

  """
  column_names = spotify.columns.tolist()

  audio_feats_scaled = scaler.transform([audio_feats])
  audio_feats_scaled_df = pd.DataFrame(audio_feats_scaled, columns=column_names)

  ## Nearest Neighbors model
  nn = NearestNeighbors(n_neighbors=6, algorithm='kd_tree')
  nn.fit(spotify_scaled)

  # prediction 
  prediction = nn.kneighbors(audio_feats_scaled)

  simlar_songs_index = prediction[1][0][1:].tolist()
  
  similar_songs = []
  
  for i in simlar_songs_index:
    song = identify['track_name'].iloc[i]
    similar_songs.append(song)

  similar_songs_indexes = []

  for song in similar_songs:
    recommened_song_index = identify[identify['track_name'] == song].index[0]
    similar_songs_indexes.append(recommened_song_index)

  similar_songs_features = []

  for index in similar_songs_indexes:
    list_of_feats = spotify.iloc[index].tolist()
    similar_songs_features.append(list_of_feats)

  similar_feats_scaled = scaler.transform(similar_songs_features)
  similar_feats_scaled_df = pd.DataFrame(similar_feats_scaled, columns=column_names)

  similar_feats_averaged = []
  
  for col in column_names:
    avg = similar_feats_scaled_df[col].mean()
    similar_feats_averaged.append(avg)

  similar_feats_averaged_df = pd.DataFrame([similar_feats_averaged], columns=column_names)

  visual_df = pd.concat([audio_feats_scaled_df, similar_feats_averaged_df], ignore_index=True)

  return visual_df


print('------------------------')
print(dataframe_for_visualizations(test_audio_features))
