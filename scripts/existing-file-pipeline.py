import os, sys; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) # changing to root directery
import pandas as pd 
from config.config import audio_features

def standardize_data(df): 
    audio_features = audio_features
    columns = ['song', 'artist', *audio_features] # unpacking audio features

def get_info(input_file1, input_file2):
    df1 = pd.read_csv(input_file1) 
    df2 = pd.read_csv(input_file2)