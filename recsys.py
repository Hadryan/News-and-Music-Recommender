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

def getNewsRecommendationW2V(fileName, email, preference, fileRatings,alreadyLiked):
    userNews = []  # Contiene una lista di news per un utente con [email, link news, cosine]
    query = calculate_centroid(preference,1)
    with open(fileName, 'r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter=';')
        for row in reader:

            if row[5] and len(row[5]) > 10:
                news = []  # creo lista vuota che ocnterrà le info dell'utente per una determinata news

                pp_news = pp.preprocess_string(row[5],
                                               CUSTOM_FILTERS)  # Faccio il pre-processing della descrizione della notizia

                if len(pp_news) > 2:
                    #print(pp_news)
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
            if not (news[1] in alreadyLiked):
                myfile.write(news[0] + ";")  # email
                myfile.write(news[1] + ";")  # link
                myfile.write('{} \n'.format(news[2]))  # cosine similarity
                # print(pp_news) # descrizione pre-processata

    print('Scrittura in ' + fileRatings + ' avvenuta per ' + email + '!')
    myfile.close()

    return ''

def getNewsRecommendationFastText(fileName, email, preference, fileRatings,alreadyLiked):
    userNews = []  # Contiene una lista di news per un utente con [email, link news, cosine]
    query = calculate_centroid(preference, 1)
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
            if not (news[1] in alreadyLiked):
                myfile.write(news[0] + ";")  # email
                myfile.write(news[1] + ";")  # link
                myfile.write('{} \n'.format(news[2]))  # cosine similarity
                # print(pp_news) # descrizione pre-processata

    print('Scrittura in ' + fileRatings + ' avvenuta per ' + email + '!')
    myfile.close()

    return ''

def getNewsRecommendationDoc2Vec(fileName, email, preference, fileRatings,alreadyLiked):
    userNews = []  # Contiene una lista di news per un utente con [email, link news, cosine]
    query = calculate_centroid(preference,1)
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
            if not (news[1] in alreadyLiked):
                myfile.write(news[0] + ";")  # email
                myfile.write(news[1] + ";")  # link
                myfile.write('{} \n'.format(news[2]))  # cosine similarity
                # print(pp_news) # descrizione pre-processata

    print('Scrittura in ' + fileRatings + ' avvenuta per ' + email + '!')
    myfile.close()

    return ''

def getNewsRecommendationLsi(fileName, email, query, fileRatings,alreadyLiked):

    #query = "elon musk tesla tecnologia spacex hyperloop viaggiare spazio scienza galileo hardware droni marte"
    textCorpus = []  # Contiene una lista di news per un utente con [email, link news, cosine]
    textCorpus.append(query)
    newsdf = []
    #print(query)
    with open(fileName, 'r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter=';')
        for row in reader:

            if row[5] and len(row[5]) > 10:
                pp_news = pp.preprocess_string(row[5],CUSTOM_FILTERS)  # Faccio il pre-processing della descrizione della notizia

                if len(pp_news) > 2:
                # processed_corpus.append(pp_news)
                    textCorpus.append(row[5])
                    newsdf.append(row)

    processed_corpus = preprocess_documents(textCorpus)

    dictionary = gensim.corpora.Dictionary(processed_corpus)
    bow_corpus = [dictionary.doc2bow(text) for text in processed_corpus]

    tfidf = gensim.models.TfidfModel(bow_corpus, smartirs='npu')
    corpus_tfidf = tfidf[bow_corpus]

    lsiModel = gensim.models.LsiModel(corpus_tfidf, num_topics=1000)
    index = gensim.similarities.MatrixSimilarity(lsiModel[corpus_tfidf])
    new_doc = gensim.parsing.preprocessing.preprocess_string(query)
    new_vec = dictionary.doc2bow(new_doc)
    vec_bow_tfidf = tfidf[new_vec]
    sims = index[vec_bow_tfidf]

    for s in sorted(enumerate(sims), key=lambda item: -item[1])[:10]:

        if not (newsdf[s[0] -1][1] in alreadyLiked):
            with io.open(fileRatings, "a", encoding="utf-8") as myfile:
                myfile.write(email + ";")
                myfile.write(newsdf[s[0] -1][1] + ";")
                myfile.write('{} \n'.format(s[1]))

            myfile.close()
    file.close()

    return ''

def profileBuilder(file, email,Technique):
    # Apertura file JSON
    f = open('fileMyrror/' + file)
    # Ritorna JSON come oggetto
    data = json.load(f)
    # Chiusura del file JSON
    f.close()
    # Lista contenente le preferenze positive dell'utente
    preferenceIT = []
    preferenceEN = []
    queryIT = ""
    queryEN = ""
    alreadyLiked = []

    # Itero attraverso la lista JSON
    for i in data['interests']:

        if i['source'] == 'news_feedback':
            if 'Like:' in i['value']:
                _url = i['value'].replace('Like:', '')
                alreadyLiked.append(_url)
            elif 'Dislike:' in i['value']:
                _url = i['value'].replace('Disike:', '')
                alreadyLiked.append(_url)

        # Se abbiamo una preferenza positiva dell'utente per le news
        if i['source'] == 'news_preference' and 'Like:' in i['value'] and not ('Dislike:' in i['value']) and \
                not (i['value'].startswith('URL:')):
            data = i['value'].replace('Like:', '').replace('Topic:', '')
            if len(data) > 2:
                if data.endswith('::it'):
                    preferenceIT.append(data.replace('::it', ''))
                    queryIT += " " + data.replace('::it', '')
                elif data.endswith('::en'):
                    preferenceEN.append(data.replace('::en', ''))
                    queryEN += " " + data.replace('::en', '')
                else:
                    preferenceIT.append(data)
                    preferenceEN.append(data)
                    queryEN += " " + data
                    queryIT += " " + data

    if len(queryEN) > 10 and len(preferenceEN) >= 2:
        #preferencePositiveEN = preprocess_documents(queryEN)
        preferencePositiveEN =  np.hstack(queryEN)
        if Technique == 1:

            getNewsRecommendationW2V('newsEN.csv', email, preferencePositiveEN, "rec_en.csv", alreadyLiked)
        elif Technique == 2:
            getNewsRecommendationFastText('newsEN.csv', email, preferencePositiveEN, "rec_en.csv", alreadyLiked)
        elif Technique == 3:
            getNewsRecommendationDoc2Vec('newsEN.csv', email, preferencePositiveEN, "rec_en.csv", alreadyLiked)
        else:
            getNewsRecommendationLsi('newsEn.csv', email, queryEN, "rec_en.csv", alreadyLiked)

    if len(queryIT) > 10 and len(preferenceIT) >= 2:
        #preferencePositiveIT = preprocess_documents(queryIT)
        preferencePositiveIT = np.hstack(queryIT)
        if Technique == 1:
            getNewsRecommendationW2V('newsIta.csv', email, preferencePositiveIT, "rec_it.csv", alreadyLiked)  # ITA
        elif Technique == 2:
            getNewsRecommendationFastText('newsIta.csv', email, preferencePositiveIT, "rec_it.csv", alreadyLiked)  # ITA
        elif Technique == 3:
            getNewsRecommendationDoc2Vec('newsIta.csv', email, preferencePositiveIT, "rec_it.csv", alreadyLiked)  # ITA
        else:
            getNewsRecommendationLsi('newsIta.csv', email, queryIT, "rec_it.csv", alreadyLiked)  # ITA

        # Raccomandazioni





def mainRun():
    Technique = 3
    try:
        f = open('rec_it.csv', 'r+')
        f.truncate(0)
        f = open('rec_en.csv', 'r+')
        f.truncate(0)
    except:
        print("file to be created")
        #f = open('rec_it.csv', 'w')
    # Lettura file degli utenti di Myrror
    for (dirpath, dirnames, filenames) in walk("fileMyrror"):
        for file in filenames:
            if file.startswith('past_'):
                email = file.split("past_", 1)[1]
                email = os.path.splitext(email)[0]

                profileBuilder(file, email,Technique)

# Utilizzo Word2Vec
wv = api.load('word2vec-google-news-300')

# Utilizzo FastText
ft = load_facebook_model('fasttext/wiki.simple.bin')

# Utilizzo Doc2Vec
dv = Doc2Vec.load('doc2vec/doc2vec.bin')

mainRun()