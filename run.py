from enum import Enum
import json
import io
import csv
import gensim
import gensim.downloader as api
import gensim.parsing.preprocessing as pp
from gensim.parsing.preprocessing import preprocess_documents
import numpy as np
import pandas as pd
from scipy import spatial
from os import walk
import os
from operator import itemgetter
from pprint import pprint as print
from gensim.models.fasttext import FastText, load_facebook_model
from gensim.test.utils import datapath
from gensim.models.doc2vec import Doc2Vec


class Technique(Enum):
    WORD_2_VEC = 1
    LSI = 2
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


def calculate_centroid(text, modeApi):
    vectors = list()
    for word in text:
        try:
            if modeApi == 1:  # Word2Vec
                vector = wv[word]
                vectors.append(vector)
            elif modeApi == 2:  # FastText
                vector = ft[word]
                vectors.append(vector)
            elif modeApi == 3:  # Doc2Vec
                vector = dv[word]
                vectors.append(vector)
        except Exception:
            # print('Skipping word {}'.format(word))
            continue
    if vectors:
        return np.asarray(vectors).mean(axis=0)
    return np.array([])


def getNewsRecommendationW2V(fileName, email, query, fileRatings):
    userNews = []  # Contiene una lista di news per un utente con [email, link news, cosine]

    with open(fileName, 'r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter=';')
        for row in reader:

            if row[5] and len(row[5]) > 10:
                news = []  # creo lista vuota che ocnterrà le info dell'utente per una determinata news

                pp_news = pp.preprocess_string(row[5],
                                               CUSTOM_FILTERS)  # Faccio il pre-processing della descrizione della notizia

                if len(pp_news) > 2:

                    # Calcolo il centroide per ogni news
                    newsVector = calculate_centroid(pp_news, 1)

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

    # Scrivo nel file i ratings per le news dell'utente
    with io.open(fileRatings, "a", encoding="utf-8") as myfile:

        for news in userNews:
            myfile.write(news[0] + ";")  # email
            myfile.write(news[1] + ";")  # link
            myfile.write('{} \n'.format(news[2]))  # cosine similarity
            # print(pp_news) # descrizione pre-processata

    print('Scrittura in ' + fileRatings + ' avvenuta per ' + email + '!')
    myfile.close()

    return ''


def word2vec(file, email):
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

        '''
        1) Creare un array in cui salviamo tutti i link che l'utente ha valutato positivamente
        Nella lettura degli articoli presenti nel file delle news controlliamo che gli articoli che già piacciono all'utente
        non vengano letti e reinseriti nel file di 'ratings'
        2) Il file 'ratings' aperto in scrittura deve essere riscritto da capo ogni volta?
        '''

        # Se abbiamo una preferenza positiva dell'utente per le news
        if i['source'] == 'news_preference' and 'Like:' in i['value'] and not ('Dislike:' in i['value']) and \
                not (i['value'].startswith('URL:')):
            data = i['value'].replace('Like:', '').replace('Topic:', '')

            data = pp.preprocess_string(data,
                                        CUSTOM_FILTERS)  # Faccio il pre-processing della preferenza dell'utente

            preferencePositive.append(data)

    if preferencePositive and preferencePositive != [] and len(preferencePositive) >= 2:
        # Trasformo la lista in un array numpy e riduco la dimensionalità ad un singolo vettore
        preferencePositiveArray = np.hstack(preferencePositive)

        # Calcolo il centroide delle preferenze positive dell'utente per le news
        query = calculate_centroid(preferencePositiveArray, 1)

        # Raccomandazioni
        getNewsRecommendationW2V('newsIta.csv', email, query, "rec_Wv_It.csv")  # ITA
        getNewsRecommendationW2V('newsEN.csv', email, query, "rec_Wv_En.csv")  # EN
        print('')


def getNewsRecommendationFastText(fileName, email, query, fileRatings):
    userNews = []  # Contiene una lista di news per un utente con [email, link news, cosine]

    with open(fileName, 'r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter=';')
        for row in reader:

            if row[5] and len(row[5]) > 10:
                news = []  # creo lista vuota che ocnterrà le info dell'utente per una determinata news

                pp_news = pp.preprocess_string(row[5],
                                               CUSTOM_FILTERS)  # Faccio il pre-processing della descrizione della notizia

                # Calcolo il centroide per ogni news
                newsVector = calculate_centroid(pp_news, 2)

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

    # Scrivo nel file i ratings per le news dell'utente
    with io.open(fileRatings, "a", encoding="utf-8") as myfile:

        for news in userNews:
            myfile.write(news[0] + ";")  # email
            myfile.write(news[1] + ";")  # link
            myfile.write('{} \n'.format(news[2]))  # cosine similarity
            # print(pp_news) # descrizione pre-processata

    print('Scrittura in ' + fileRatings + ' avvenuta per ' + email + '!')
    myfile.close()

    return ''


def fastText(file, email):
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

        '''
        1) Creare un array in cui salviamo tutti i link che l'utente ha valutato positivamente
        Nella lettura degli articoli presenti nel file delle news controlliamo che gli articoli che già piacciono all'utente
        non vengano letti e reinseriti nel file di 'ratings'
        2) Il file 'ratings' aperto in scrittura deve essere riscritto da capo ogni volta?
        '''

        # Se abbiamo una preferenza positiva dell'utente per le news
        if i['source'] == 'news_preference' and 'Like:' in i['value'] and not ('Dislike:' in i['value']) and \
                not (i['value'].startswith('URL:')):

            data = i['value'].replace('Like:', '').replace('Topic:', '')

            if len(data) > 5:
                data = pp.preprocess_string(data,
                                            CUSTOM_FILTERS)  # Faccio il pre-processing della preferenza dell'utente

            preferencePositive.append(data)

    if preferencePositive and preferencePositive != [] and len(preferencePositive) >= 2:
        # Trasformo la lista in un array numpy e riduco la dimensionalità ad un singolo vettore
        preferencePositiveArray = np.hstack(preferencePositive)

        # Calcolo il centroide delle preferenze positive dell'utente per le news
        query = calculate_centroid(preferencePositiveArray, 2)

        # Raccomandazioni
        getNewsRecommendationFastText('newsIta.csv', email, query, "rec_Ft_It.csv")  # ITA
        getNewsRecommendationFastText('newsEN.csv', email, query, "rec_Ft_En.csv")  # EN
        print('')


def getNewsRecommendationDoc2Vec(fileName, email, query, fileRatings):
    userNews = []  # Contiene una lista di news per un utente con [email, link news, cosine]

    with open(fileName, 'r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter=';')
        for row in reader:

            if row[5] and len(row[5]) > 10:
                news = []  # creo lista vuota che ocnterrà le info dell'utente per una determinata news

                pp_news = pp.preprocess_string(row[5],
                                               CUSTOM_FILTERS)  # Faccio il pre-processing della descrizione della notizia

                if len(pp_news) > 2:

                    # Calcolo il centroide per ogni news
                    newsVector = calculate_centroid(pp_news, 3)

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

    # Scrivo nel file i ratings per le news dell'utente
    with io.open(fileRatings, "a", encoding="utf-8") as myfile:

        for news in userNews:
            myfile.write(news[0] + ";")  # email
            myfile.write(news[1] + ";")  # link
            myfile.write('{} \n'.format(news[2]))  # cosine similarity
            # print(pp_news) # descrizione pre-processata

    print('Scrittura in ' + fileRatings + ' avvenuta per ' + email + '!')
    myfile.close()

    return ''


def doc2vec(file, email):
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

        '''
        1) Creare un array in cui salviamo tutti i link che l'utente ha valutato positivamente
        Nella lettura degli articoli presenti nel file delle news controlliamo che gli articoli che già piacciono all'utente
        non vengano letti e reinseriti nel file di 'ratings'
        2) Il file 'ratings' aperto in scrittura deve essere riscritto da capo ogni volta?
        '''

        # Se abbiamo una preferenza positiva dell'utente per le news
        if i['source'] == 'news_preference' and 'Like:' in i['value'] and not ('Dislike:' in i['value']) and \
                not (i['value'].startswith('URL:')):

            data = i['value'].replace('Like:', '').replace('Topic:', '')

            if len(data) > 5:
                data = pp.preprocess_string(data,
                                            CUSTOM_FILTERS)  # Faccio il pre-processing della preferenza dell'utente

            preferencePositive.append(data)

    if preferencePositive and preferencePositive != [] and len(preferencePositive) >= 2:
        # Trasformo la lista in un array numpy e riduco la dimensionalità ad un singolo vettore
        preferencePositiveArray = np.hstack(preferencePositive)

        # Calcolo il centroide delle preferenze positive dell'utente per le news
        query = calculate_centroid(preferencePositiveArray, 3)

        # Raccomandazioni
        getNewsRecommendationDoc2Vec('newsIta.csv', email, query, "rec_Dv_It.csv")  # ITA
        getNewsRecommendationDoc2Vec('newsEN.csv', email, query, "rec_Dv_En.csv")  # EN
        print('')


# ----------------------------------------------------------------------------------------------------------------------------------------------

# Utilizzo Word2Vec
wv = api.load('word2vec-google-news-300')

# Utilizzo FastText
ft = load_facebook_model('fasttext/wiki.simple.bin')

# Utilizzo Doc2Vec
dv = Doc2Vec.load('doc2vec/doc2vec.bin')


def mainRun():
    # Lettura file degli utenti di Myrror
    for (dirpath, dirnames, filenames) in walk("fileMyrror"):
        for file in filenames:
            if file.startswith('past_'):
                email = file.split("past_", 1)[1]
                email = os.path.splitext(email)[0]
                word2vec(file, email)
                fastText(file, email)
                doc2vec(file, email)


mainRun()
