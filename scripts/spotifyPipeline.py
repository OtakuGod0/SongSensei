
import sys; sys.path.append('.') # adding path of root directiory for module import to avoid any errors
import pandas as pd 
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
from config.api import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET
from urllib.error import HTTPError

# Defining Spotify object
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri="http://localhost:8888/callback",  # Must match the URI you set on spotify api dashboard
    scope="user-library-read",
    cache_path=".spotify_cache"
))

def get_info(song: str) -> dict:
    '''
        Get song information (release_date, spotify_id, popularity) and audio features
        ['danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'time_signature']
        
        args: 
            song -> name of the song to get info
        returns: 
            song_data -> distionary with all the information
    '''
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

def getFeatures(input_df: pd.DataFrame) -> pd.DataFrame: 
    '''
        input a pd.DataFrame of list of songs and get its features using spotify api
        args: 
            input_df -> pd.DataFrame of list of songs to get info of
            
        returns: 
            featured_df -> pd.DataFrame of song with its features
    '''
    
    # Initialize an empty list to df = pd.read_csv('combined.csv')accumulate rows
    rows = []
    
    data_count = 0 # retrived data count 
    
    # iterating over each row of data and collecting their information from spotify api
    for _, row in input_df.iterrows():
        sleep_count = 60 # sleep count for retry error 429 to many request
        while True: # For retry (error 429)
            try: 
                # Getting info from Spotify 
                info = get_info(f"{row['song']} by {row['artist']}")
                
                # Appending song name and artist to the info dictionary
                info.update({'song': row['song'], 'artist': row['artist']})
            
                # Accumulate the info dictionary in a list
                rows.append(info)
        
                # Retrived data count 
                data_count += 1
                print(f"{data_count} data retrived", end='\r') #overwrite the previous output

                # Delaying by 1s to lighten load
                time.sleep(1)
                
                # Break from infinite while loop to move on to next row
                break
                
            # for catching to many request (429) error
            except HTTPError as http_err:
                if http_err.code == 429: # Handling to many request 
                    print("request limit reached")

                    # saving accumulated data incase of failure
                    if sleep_count == 60: # checking if first loop
                        print("Saving accumulated data in case of failure")
                        tmp_df = pd.DataFrame(rows)
                        try:
                            tmp_df.to_csv('tmp.csv', index=False)
                        except PermissionError as e:
                            print(f"Permission error while writing to tmp.csv: {e}")
                            
                    # Sleeping 
                    print(f"sleeping for {sleep_count} seconds")
                    time.sleep(sleep_count)

                    # Exponentialy increasing sleep_count to tackle error 429 in next loop 
                    sleep_count = sleep_count**2 

                    continue
                
                elif http_err.code == 400: 
                    print('Bad Request: ')
                    print(f'song: {row['song']}, artist: {row['artist']}') 
                    print('Skipping this row')
                    
                    continue
                else:
                    print(f"HTTP Error: {http_err}")
                    break
    
    
    # Convert accumulated rows to DataFrame at once
    featured_df = pd.DataFrame(rows)
    return featured_df


def store_data(input_df, output_file): 
    input_df.to_csv(output_file, index = False)


if __name__ == '__main__': 
    """
        For unit testing
    """
    
    if len(sys.argv) > 1: 
        song_name = sys.argv[1]
        artist_name = sys.argv[2]
        
        
        # Debugging
        print(song_name, artist_name)
        
        df = pd.DataFrame({'song': [song_name], 'artist': [artist_name]})
        
        featured_df = getFeatures(df)
        
        print(featured_df)