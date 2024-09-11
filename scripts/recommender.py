import pandas as pd
import random
import sys

df = pd.read_csv("sample.csv") # file needs to be changed no longer available 

def recommend(*songs):
    recommended_songs = []
    for song in songs:
        try: 
            # Finding Cluster of the song
            cluster = df[df['song'] == song]['Cluster'].values[0]

            # Songs of same cluster
            similar_song = df[df['Cluster'] == cluster]

            recommended_songs.append(similar_song.sample(n = 5)['song'].values) # recommending 5 songs of same cluster
            
        except IndexError: # Catch unknown songs
            print("Song not found in database")


    random.shuffle(recommended_songs)
    return recommended_songs


if __name__ == '__main__':
    if len(sys.argv) > 0:
        recommend(*sys.argv[1:]) # unpacking the argv list and passing to recommend
    else:
        print("No argument was passed")
