from enum import Enum
import json
import io
import csv
import gensim.downloader as api
import gensim.parsing.preprocessing as pp
import numpy as np
import pandas as pd
from scipy import spatial
from os import walk
import os
from operator import itemgetter


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
            # print('Skipping word {}'.format(word))
            continue
    if vectors:
        return np.asarray(vectors).mean(axis=0)
    return np.array([])


def getNewsRecommendation(fileName, email, query):

    userNews = []  # Contiene una lista di news per un utente con [email, link news, cosine]

    with open(fileName, 'r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter=';')
        for row in reader:

            if row[5] and len(row[5]) > 10:
                news = [] # creo lista vuota che ocnterrà le info dell'utente per una determinata news

                pp_news = pp.preprocess_string(row[5],
                                               CUSTOM_FILTERS)  # Faccio il pre-processing della descrizione della notizia

                # Calcolo il centroide per ogni news
                newsVector = calculate_centroid(pp_news)

                # Calcolo la cosine similarity tra il centroide della news ed il centroide della preferenza dell'utente
                cos_sim = 1 - spatial.distance.cosine(query, newsVector)

                # Info sulla news
                news.append(email)  # email
                news.append(row[1])  # link
                news.append(cos_sim)  # cosine similarity

                # Inserisco la news in una lista di news
                userNews.append(news)

    file.close()

    # Ordino in ordine decrescente la cosine similarity
    userNews.sort(key=itemgetter(2), reverse=True)

    #Scrivo nel file i ratings per le news dell'utente
    with io.open("ratings.csv", "a", encoding="utf-8") as myfile:

        for news in userNews:
            myfile.write(news[0] + ";")
            myfile.write(news[1] + ";")
            myfile.write('{} \n'.format(news[2]))
            # print(pp_news) # descrizione pre-processata

    myfile.close()

    return ''


def readProfile(file, email):

    # Apertura file JSON
    f = open('fileMyrror/' + file)

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

    if preferencePositive and preferencePositive != [] and len(preferencePositive) >= 2:
        # Trasformo la lista in un array numpy e riduco la dimensionalità ad un singolo vettore
        preferencePositiveArray = np.hstack(preferencePositive)

        # Calcolo il centroide delle preferenze positive dell'utente per le news
        query = calculate_centroid(preferencePositiveArray)

        # Lettura descrizione degli articoli presenti nel file news.csv
        allNews = getNewsRecommendation('newsIta.csv', email, query)


# Utilizzo Word2Vec
wv = api.load('word2vec-google-news-300')

# Lettura file degli utenti di Myrror
for (dirpath, dirnames, filenames) in walk("fileMyrror"):
    for file in filenames:
        if file.startswith('past_'):
            email = file.split("past_", 1)[1]
            email = os.path.splitext(email)[0]
            readProfile(file, email)
