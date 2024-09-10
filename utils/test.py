import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) # changing to root directery

from config.config import audio_features

print(audio_features)
