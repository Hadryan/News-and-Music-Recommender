import json
import io
import csv
import gensim
import gensim.downloader as api
import gensim.parsing.preprocessing as pp
import numpy as np
from scipy import spatial
from os import walk
import os
from operator import itemgetter
from gensim.models.fasttext import load_facebook_model
from gensim.models.doc2vec import Doc2Vec, TaggedDocument

# Pre-processing operations to apply
CUSTOM_FILTERS = [lambda x: x.lower(), pp.strip_tags,
                  pp.strip_punctuation,
                  # pp.remove_stopwords,
                  # pp.split_alphanum,
                  pp.strip_multiple_whitespaces]

NEWS_FILTERS = [lambda x: x.lower(), pp.strip_tags,
                pp.strip_punctuation,
                pp.split_alphanum, pp.strip_multiple_whitespaces,
                pp.strip_numeric]


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


def getNewsRecommendationW2V(fileName, email, preference, fileRatings, alreadyLiked):
    userNews = []  # Contiene una lista di news per un utente con [email, link news, cosine]
    query = calculate_centroid(preference, 1)
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

        i = 0
        for news in userNews:
            if i > 5:
                break

            if not (news[1] in alreadyLiked):
                myfile.write(news[0] + ";")  # email
                myfile.write(news[1] + ";")  # link
                myfile.write('{} \n'.format(news[2]))  # cosine similarity
                # print(pp_news) # descrizione pre-processata
                i = i + 1

    print('Scrittura in ' + fileRatings + ' avvenuta per ' + email + '!')
    myfile.close()

    return ''


def getNewsRecommendationFastText(fileName, email, preference, fileRatings, alreadyLiked):
    userNews = []  # Contiene una lista di news per un utente con [email, link news, cosine]
    query = calculate_centroid(preference, 2)
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
        i = 0

        for news in userNews:
            if i > 10:
                break

            if not (news[1] in alreadyLiked):
                myfile.write(news[0] + ";")  # email
                myfile.write(news[1] + ";")  # link
                myfile.write('{} \n'.format(news[2]))  # cosine similarity
                # print(pp_news) # descrizione pre-processata

                i = i + 1

    print('Scrittura in ' + fileRatings + ' avvenuta per ' + email + '!')
    myfile.close()

    return ''


def getNewsRecommendationDoc2Vec(fileName, email, preference, fileRatings, alreadyLiked):
    userNews = []  # Contiene una lista di news per un utente con [email, link news, cosine]
    documents = []
    links = []
    query = calculate_centroid(preference, 3)
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

    with io.open(fileRatings, "a", encoding="utf-8") as myfile:
        i = 0
        for news in userNews:
            if i > 6:
                break

            if not (news[1] in alreadyLiked):
                myfile.write(news[0] + ";")  # email
                myfile.write(news[1] + ";")  # link
                myfile.write('{} \n'.format(news[2]))  # cosine similarity
                # print(news[1]) # descrizione pre-processata

                i = i + 1

    print('Scrittura in ' + fileRatings + ' avvenuta per ' + email + '!')
    myfile.close()

    return ''


def getNewsRecommendationLsi(fileName, email, query, fileRatings, alreadyLiked, dim):
    processed_corpus = [query]
    newsdf = []

    with open(fileName, 'r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter=';')

        for row in reader:
            if row[5] and len(row[5]) > 10:
                pp_news = pp.preprocess_string(row[5],
                                               CUSTOM_FILTERS)  # Faccio il pre-processing della descrizione della notizia

                if len(pp_news) >= 2:
                    processed_corpus.append(pp_news)
                    newsdf.append(row)

    dictionary = gensim.corpora.Dictionary(processed_corpus)
    bow_corpus = [dictionary.doc2bow(text) for text in processed_corpus]

    tfidf = gensim.models.TfidfModel(bow_corpus, smartirs='npu')
    corpus_tfidf = tfidf[bow_corpus]

    if dim > 300:
        num_topics = 200
    else:
        num_topics = 100

    if dim > 1000:
        num_topics = 200

    # 2200 limit for words

    lsiModel = gensim.models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=num_topics, chunksize=100)
    # print(lsiModel.print_topics(num_topics=num_topics,num_words=5))
    index = gensim.similarities.MatrixSimilarity(lsiModel[corpus_tfidf])

    new_vec = dictionary.doc2bow(query)

    vec_bow_tfidf = tfidf[new_vec]
    sims = index[vec_bow_tfidf]

    for s in sorted(enumerate(sims), key=lambda item: -item[1])[:10]:

        if not (newsdf[s[0] - 1][1] in alreadyLiked):
            with io.open(fileRatings, "a", encoding="utf-8") as myfile:
                myfile.write(email + ";")
                myfile.write(newsdf[s[0] - 1][1] + ";")
                myfile.write('{} \n'.format(s[1]))

            myfile.close()
    file.close()

    print('Scrittura in ' + fileRatings + ' avvenuta per ' + email + '!')

    return ''


def profileBuilder(file, email, Technique):
    # Apertura file JSON
    f = open('fileMyrror/' + file)

    # Ritorna JSON come oggetto
    data = json.load(f)

    # Chiusura del file JSON
    f.close()
    query = ""

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

                    data = data.replace('::it', '')
                    pp_news = pp.preprocess_string(pp.strip_short(data, minsize=3),
                                                   CUSTOM_FILTERS)  # Faccio il pre-processing della descrizione della notizia

                    preferenceIT.append(pp_news)
                    queryIT += " " + data.replace('::it', '')

                elif data.endswith('::en'):
                    data = data.replace('::en', '')
                    pp_news = pp.preprocess_string(data, CUSTOM_FILTERS)
                    preferenceEN.append(pp_news)
                    queryEN += " " + data

                else:
                    preferenceIT.append(data)
                    preferenceEN.append(data)
                    query += " " + data
                    query += " " + data

    dim = len(queryEN)
    if dim < 10:
        queryEN += query
    dim = len(queryEN)

    # INGLESE
    if dim > 10 and len(preferenceEN) >= 1:
        preferencePositiveEN = pp.preprocess_string(queryEN, CUSTOM_FILTERS)

        if Technique == 1:  # Word2Vec
            getNewsRecommendationW2V('newsEN.csv', email, preferencePositiveEN, "rec_news_w2v_en.csv", alreadyLiked)
        elif Technique == 2:  # FastText
            getNewsRecommendationFastText('newsEN.csv', email, preferencePositiveEN, "rec_news_ft_en.csv", alreadyLiked)
        elif Technique == 3:  # Doc2Vec
            getNewsRecommendationDoc2Vec('newsEN.csv', email, preferencePositiveEN, "rec_news_d2v_en.csv", alreadyLiked)
        elif Technique == 4:  # Lsi
            getNewsRecommendationLsi('newsEN.csv', email, preferencePositiveEN, "rec_news_lsi_en.csv", alreadyLiked, dim)

    # ITALIANO
    dim = len(queryIT)
    if dim < 10:
        queryIT += query
    if len(queryIT) > 10 and len(preferenceIT) >= 2:
        preferencePositiveIT = pp.preprocess_string(queryIT, CUSTOM_FILTERS)

        if Technique == 1:  # Word2Vec
            getNewsRecommendationW2V('newsIta.csv', email, preferencePositiveIT, "rec_news_w2v_it.csv", alreadyLiked)
        elif Technique == 2:  # FastText
            getNewsRecommendationFastText('newsIta.csv', email, preferencePositiveIT, "rec_news_ft_it.csv", alreadyLiked)
        elif Technique == 3:  # Doc2Vec
            getNewsRecommendationDoc2Vec('newsIta.csv', email, preferencePositiveIT, "rec_news_d2v_it.csv", alreadyLiked)
        elif Technique == 4:  # Lsi
            getNewsRecommendationLsi('newsIta.csv', email, preferencePositiveIT, "rec_it.csv", alreadyLiked, dim)


def mainRun(Technique):
    if Technique == 1:  # Word2Vec
        print("\nTecnica di raccomandazione news: Word2Vec")
        try:
            f = open('rec_news_w2v_it.csv', 'r+')
            f.truncate(0)
            f = open('rec_news_w2v_en.csv', 'r+')
            f.truncate(0)
        except:
            print("Creazione file rec_news_w2v_it.csv...")
            print("Creazione file rec_news_w2v_en.csv...")

    elif Technique == 2:  # FastText
        print("\nTecnica di raccomandazione news: FastText")
        try:
            f = open('rec_news_ft_it.csv', 'r+')
            f.truncate(0)
            f = open('rec_news_ft_en.csv', 'r+')
            f.truncate(0)
        except:
            print("Creazione file rec_news_ft_it.csv...")
            print("Creazione file rec_news_ft_en.csv...")

    elif Technique == 3:  # Doc2Vec
        print("\nTecnica di raccomandazione news: Doc2Vec")
        try:
            f = open('rec_news_d2v_it.csv', 'r+')
            f.truncate(0)
            f = open('rec_news_d2v_en.csv', 'r+')
            f.truncate(0)
        except:
            print("Creazione file rec_news_d2v_it.csv...")
            print("Creazione file rec_news_d2v_en.csv...")

    elif Technique == 4:  # Lsi
        print("\nTecnica di raccomandazione news: Lsi")
        try:
            f = open('rec_news_lsi_it.csv', 'r+')
            f.truncate(0)
            f = open('rec_news_lsi_en.csv', 'r+')
            f.truncate(0)
        except:
            print("Creazione file rec_news_lsi_it.csv...")
            print("Creazione file rec_news_lsi_en.csv...")

    # Lettura file degli utenti di Myrror
    for (dirpath, dirnames, filenames) in walk("fileMyrror"):
        for file in filenames:
            if file.startswith('past_'):
                email = file.split("past_", 1)[1]
                email = os.path.splitext(email)[0]
                profileBuilder(file, email, Technique)


# Utilizzo Word2Vec
wv = api.load('word2vec-google-news-300')

# Utilizzo FastText
ft = load_facebook_model('fasttext/wiki.simple.bin')

# Utilizzo Doc2Vec
dv = Doc2Vec.load('doc2vec/doc2vec.bin')

# mainRun(1)
