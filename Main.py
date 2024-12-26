import uuid
from typing import Sequence

import lyricsgenius
from elasticsearch import Elasticsearch
from uuid import uuid4
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline


def standardize_lyrics(lyrics: str, pipe) -> Sequence[str]:


    lyrics = lyrics[lyrics.find("Lyrics"):]
    lyrics = lyrics.replace("\n", " ")
    lyrics = lyrics.replace("Embed", "")
    lyrics = lyrics.replace("You might also like", "")
    lyrics = lyrics.replace("Lyrics", "")

    translated_lyrics = ''
    chunks = split_string(lyrics)
    for chunk in chunks: 
        translated_lyrics += pipe(chunk)[0].get('translation_text')

    return translated_lyrics

def split_string(string, chunk_size=500):
    return [string[i:i+chunk_size] for i in range(0, len(string), chunk_size)]


from transformers import pipeline
pipe = pipeline("translation", model="Helsinki-NLP/opus-mt-tc-big-he-en")

cloud_id = "redacted"
api_key = "redacted"
es = Elasticsearch(cloud_id=cloud_id, api_key=api_key)

token = "redacted"
genius = lyricsgenius.Genius(token)

genius.remove_section_headers = True

artist = genius.search_artist("Dudu Tassa - דודו טסה")

for song in artist.songs:
    doc = {
        "title": song.title,
        "lyrics": standardize_lyrics(song.lyrics, pipe)
    }
    print(doc)
    es.index(index="dudusongs", id=str(uuid4()), document=doc)
