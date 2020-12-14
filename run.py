from enum import Enum
import json

import csv
import gensim.downloader as api
import gensim.parsing.preprocessing as pp
import numpy as np
import pandas as pd
from gensim.models.doc2vec import Doc2Vec
from gensim.models.fasttext import load_facebook_model
from lenskit.datasets import ML1M
from scipy import spatial


class Technique(Enum):
    WORD_2_VEC = 1
    DOC_2_VEC = 2
    FASTTEXT = 3


################## EDIT HERE TO CHANGE CONFIGS ########################################
MIN_POSITIVE_RATING = 4  # minimum rating to consider an item as liked
NUM_OF_RECS = 10  # num of recs for each user
OUTPUT_FOLDER = '../recs/cb-word-embedding/'  # output folder
OUTPUT_FILE_NAME = 'INSERT_ALGORITHM_NAME_HERE'  # output filename (NO NEED TO ADD .csv)
DESCR = True  # set this to true to use descr
TAGS_AND_GENRES = True  # set this to true to use genres and tags
MODE = Technique.WORD_2_VEC  # edit here to change technique
#######################################################################################

NO_DESCR_TAG = '-no-descr'
DESCR_ONLY_TAG = '-descr-only'

# pre-processing operations to apply
CUSTOM_FILTERS = [lambda x: x.lower(), pp.strip_tags,
                  pp.strip_punctuation, pp.remove_stopwords,
                  pp.split_alphanum, pp.strip_multiple_whitespaces]


def calculate_centroid(text):
    vectors = list()
    for word in text:
        try:
            vector = wv[word]
            vectors.append(vector)
        except Exception:
            #print('Skipping word {}'.format(word))
            continue
    if vectors:
        return np.asarray(vectors).mean(axis=0)
    return np.array([])


def getAllNews(fileName):
    with open(fileName, 'r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter=';')
        for row in reader:
            pp_news = pp.preprocess_string(row[5],
                                           CUSTOM_FILTERS)  # Faccio il pre-processing della descrizione della notizia

            # Calcolo il centroide per ogni news
            newsVector = calculate_centroid(pp_news)

            # Calcolo la cosine similarity tra il centroide della news ed il centroide della preferenza dell'utente
            cos_sim = 1 - spatial.distance.cosine(query, newsVector)

            print(cos_sim) # cosine similarity
            print(pp_news) # descrizione pre-processata
            print(row[1]) # link
            print('\n')

    file.close()
    return ''


# Lettura file JSON
# Apertura file JSON
f = open('fileMyrror/data.json')

# Ritorna JSON come oggetto
data = json.load(f)

# Chiusura del file JSON
f.close()

# Lista contenente le preferenze positive dell'utente
preferencePositive = []

# Itero attraverso la lista JSON
for i in data['interests']:

    # Se abbiamo una preferenza positiva dell'utente per le news
    if i['source'] == 'news_preference' and 'Like:' in i['value'] and not ('Dislike:' in i['value']):
        data = i['value'].replace('Like:', '').replace('Topic:', '').split()
        preferencePositive.append(data)

# Trasformo la lista in un array numpy e riduco la dimensionalità ad un singolo vettore
preferencePositiveArray = np.hstack(preferencePositive)

# Utilizzo Word2Vec
wv = api.load('word2vec-google-news-300')

# Calcolo il centroide delle preferenze positive dell'utente per le news
query = calculate_centroid(preferencePositiveArray)

# Lettura descrizione degli articoli presenti nel file news.csv
allNews = getAllNews('newsIta.csv')


#Ordino in ordine decrescente la cosine similarity
#cosine_similarities.sort(reverse=True)


