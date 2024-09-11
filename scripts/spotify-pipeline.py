
import os 
import pandas as pd 
import numpy as np
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time


CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")


sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri="http://localhost:888/callback",  # Must match the URI you set on spotify api dashboard
    scope="user-library-read",
    cache_path=".spotify_cache"
))


df = pd.read_csv("filtered_data.csv").sample(n = 50)

def get_info(sp, song):
    # searching the song and selecting first song
    results = sp.search(q=song, limit=1, type='track')
    track = results['tracks']['items'][0]

    # retreving necessary song data from track
    song_data = {
        'release_date': track['album']['release_date'], 
        'spotify_id': track['id'], 
        'popularity': track['popularity']
    }

    # getting audio features and appending to song_data
    audio_features = sp.audio_features(song_data['spotify_id'])[0]

    # selecting only the necessary features
    features_to_select = ['danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'time_signature']
    selected_features = {key: audio_features[key] for key in features_to_select}
    song_data.update(selected_features)

    return song_data
    


def process_data(sp, input_df): 
    # Initialize an empty list to accumulate rows
    rows = []
    
    data_count = 0 # retrived data count 
    
    # iterating over each row of data and collecting their information from spotify api
    for index, row in input_df.iterrows():
        sleep_count = 60 # sleep count for retry error 429 to many request
        while True: # For retry (error 429)
            try: 
                # Getting info from Spotify 
                info = get_info(sp, f"{row['song']} by {row['artist']}")
                
                # Appending song name and artist to the info dictionary
                info.update({'song': row['song'], 'artist': row['artist']})
            
                # Accumulate the info dictionary in a list
                rows.append(info)
        
                # Retrived data count 
                data_count += 1
                print(f"{data_count} data retrived", end='\r') #overwrite the previous output

                # Break from infinite while loop to move on to next row
                break
                
            # for catching to many request (429) error
            except HTTPError as http_err:
                if http_err.response.status_code == 429: # Handling to many request 
                    print("request limit reached")

                    # saving accumulated data incase of failure
                    if sleep_count == 60: # checking if first loop
                        print("Saving accumulated data in case of failure")
                        tmp_df = pd.DataFrame(rows)
                        tmp_df.to_csv('tmp.csv', index = False)

                    # Sleeping 
                    print(f"sleeping for {sleep_count} seconds")
                    time.sleep(sleep_count)

                    # Exponentialy increasing sleep_count to tackle error 429 in next loop 
                    sleep_count = sleep_count**2 

                    continue
                else:
                    print(f"HTTP Error: {http_err}")
                    break
                    
            except Exception as e: 
                print(f"Error getting info from Spotify: {e}")
                break
    
    
    # Convert accumulated rows to DataFrame at once
    featured_df = pd.DataFrame(rows)
    return featured_df


def store_data(input_df, output_file): 
    input_df.to_csv(output_file, index = False)


