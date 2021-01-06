import json
import io
import csv
import gensim
import gensim.downloader as api
import gensim.parsing.preprocessing as pp
from gensim.parsing.preprocessing import preprocess_documents
import numpy as np
from scipy import spatial
from os import walk
import os
from operator import itemgetter
from gensim.models.fasttext import load_facebook_model
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
import pandas as pd
from gensim.corpora import Dictionary
from gensim.models import LdaModel

# pre-processing operations to apply
CUSTOM_FILTERS = [lambda x: x.lower(),
                  pp.strip_punctuation,
                  pp.strip_non_alphanum]


# Convert list to string, by joining all item in list with given separator. Returns the concatenated string
def convert_list_to_string(org_list, seperator=' '):
    return seperator.join(org_list)


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
        except Exception as ex:
            # print('Skipping word {}'.format(word))
            continue
    if vectors:
        return np.asarray(vectors).mean(axis=0)
    return np.array([])


def getMusicRecommendationDoc2Vec(fileName, email, preference, fileRatings, alreadyLiked):
    with open('artistCleanOutput.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter=',')

        genres = []
        artist = []

        riga = []
        for row in reader:
            # Scarto la prima riga
            if 'artist_mb' in row[1]:
                continue

            riga = row[2].split(";")
            genres.append(riga)
            artist.append(row[1])

    file.close()

    new_sentence_vectorized = dv.infer_vector(preference)

    # Calculate cosine similarity
    similar_sentences = dv.docvecs.most_similar(positive=[new_sentence_vectorized], topn=5)

    # Output
    output = []

    for i, v in enumerate(similar_sentences):
        index = v[0]
        output.append([email, artist[index], v[1], genres[index]])

    # df = pd.DataFrame(output)
    # pd.set_option("display.max_rows", None, "display.max_columns", None)
    # print(df)

    with io.open(fileRatings, "a", encoding="utf-8") as myfile:
        for rec in output:
            if not (rec[1].lower() in alreadyLiked):
                myfile.write(rec[0] + ";")  # email
                myfile.write(rec[1] + ";")  # artista
                myfile.write('{} \n'.format(rec[2]))  # cosine similarity
    print('Scrittura in ' + fileRatings + ' avvenuta per ' + email + '!')
    myfile.close()

    return ''


def getMusicRecommendationW2V(fileName, email, preference, fileRatings, alreadyLiked):
    userArtist = []  # Contiene una lista di artist per un utente con [email, link news, cosine]
    query = calculate_centroid(preference, 1)

    with open(fileName, 'r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter=',')

        for row in reader:

            # Scarto la prima riga
            if 'artist_mb' in row[1]:
                continue

            if row[2]:  # se il genere è valorizzato
                artist = []  # creo lista vuota che conterrà le info dell'utente per una determinata news

                # print(row[2])

                pp_genre = pp.preprocess_string(row[2],
                                                CUSTOM_FILTERS)  # Faccio il pre-processing del genere dell'artista

                pp_genre.append(row[1])

                i = 0
                if len(pp_genre) > 2 and len(preference) > 2:
                    try:
                        # Calcolo il centroide per ogni genere
                        artistVector = calculate_centroid(pp_genre, 1)

                        # Calcolo la cosine similarity tra il centroide del genere ed il centroide della preferenza dell'utente
                        cos_sim = 1 - spatial.distance.cosine(query, artistVector)

                        # Info sull'artista
                        artist.append(email)  # email
                        artist.append(row[1])  # artista
                        artist.append(cos_sim)  # cosine similarity

                        # Inserisco l'artista in una lista di artisti
                        userArtist.append(artist)
                    except:
                        # print(row)
                        i = i + 1

    file.close()
    print('Scartati: ')
    print(i)

    # Ordino in ordine decrescente la cosine similarity
    userArtist.sort(key=itemgetter(2), reverse=True)

    # Scrivo nel file i ratings per gli artisti dell'utente
    with io.open(fileRatings, "a", encoding="utf-8") as myfile:
        i = 0

        for artist in userArtist:
            if i > 10:
                break

            if not (artist[1].lower() in alreadyLiked):
                i = i + 1
                myfile.write(artist[0] + ";")  # email
                myfile.write(artist[1] + ";")  # artista
                myfile.write('{} \n'.format(artist[2]))  # cosine similarity
                # print(pp_news) # descrizione pre-processata

    print('Scrittura in ' + fileRatings + ' avvenuta per ' + email + '!')
    myfile.close()

    return ''


def getMusicRecommendationFastText(fileName, email, preference, fileRatings, alreadyLiked):
    userArtist = []  # Contiene una lista di artist per un utente con [email, link news, cosine]
    query = calculate_centroid(preference, 2)

    with open(fileName, 'r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter=',')

        i = 0
        for row in reader:

            # Scarto la prima riga
            if 'artist_mb' in row[1]:
                continue

            if row[2]:  # se il genere è valorizzato
                artist = []  # creo lista vuota che conterrà le info dell'utente per una determinata news

                pp_genre = pp.preprocess_string(row[2],
                                                CUSTOM_FILTERS)  # Faccio il pre-processing del genere dell'artista

                pp_genre.append(row[1])

                if len(pp_genre) >= 2 and len(preference) >= 2:
                    try:
                        # Calcolo il centroide per ogni genere
                        artistVector = calculate_centroid(pp_genre, 2)

                        # Calcolo la cosine similarity tra il centroide del genere ed il centroide della preferenza dell'utente
                        cos_sim = 1 - spatial.distance.cosine(query, artistVector)

                        # Info sull'artista
                        artist.append(email)  # email
                        artist.append(row[1])  # artista
                        artist.append(cos_sim)  # cosine similarity

                        # Inserisco l'artista in una lista di artisti
                        userArtist.append(artist)
                    except:
                        # print(row)
                        i = i + 1
    print(i)

    file.close()
    print('Scartati: ')

    # Ordino in ordine decrescente la cosine similarity
    userArtist.sort(key=itemgetter(2), reverse=True)

    # Scrivo nel file i ratings per gli artisti dell'utente
    with io.open(fileRatings, "a", encoding="utf-8") as myfile:
        i = 0

        for artist in userArtist:
            if i > 10:
                break

            if not (artist[1].lower() in alreadyLiked):
                i = i + 1
                myfile.write(artist[0] + ";")  # email
                myfile.write(artist[1] + ";")  # artista
                myfile.write('{} \n'.format(artist[2]))  # cosine similarity
                # print(pp_news) # descrizione pre-processata

    print('Scrittura in ' + fileRatings + ' avvenuta per ' + email + '!')
    myfile.close()

    return ''


def getMusicRecommendationLsi(fileName, email, query, fileRatings, alreadyLiked):
    textCorpus = [query]  # Contiene una lista di generi per un utente
    artistdf = []
    # print(query)
    with open(fileName, 'r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter=',')
        for row in reader:

            # Scarto la prima riga
            if 'artist_mb' in row[1]:
                continue

            if row[2]:
                pp_genre = pp.preprocess_string(row[2],
                                                CUSTOM_FILTERS)  # Faccio il pre-processing del genere dell'artista

                pp_genre.append(row[1])

                if len(pp_genre) > 2:
                    textCorpus.append(pp_genre)
                    artistdf.append(row)


    dictionary = gensim.corpora.Dictionary(textCorpus)
    bow_corpus = [dictionary.doc2bow(text) for text in textCorpus]

    tfidf = gensim.models.TfidfModel(bow_corpus, smartirs='npu')
    corpus_tfidf = tfidf[bow_corpus]

    lsiModel = gensim.models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=200, chunksize=100)
    index = gensim.similarities.MatrixSimilarity(lsiModel[corpus_tfidf])
    #new_doc = gensim.parsing.preprocessing.preprocess_string(query)
    new_vec = dictionary.doc2bow(query)
    vec_bow_tfidf = tfidf[new_vec]
    sims = index[vec_bow_tfidf]


    for s in sorted(enumerate(sims), key=lambda item: -item[1])[:10]:

        if not (artistdf[s[0] - 1][1].lower() in alreadyLiked):
            with io.open(fileRatings, "a", encoding="utf-8") as myfile:
                myfile.write(email + ";")
                myfile.write(artistdf[s[0] - 1][1] + ";")
                myfile.write('{} \n'.format(s[1]))

            myfile.close()
    file.close()

    print('Scrittura in ' + fileRatings + ' avvenuta per ' + email + '!')

    return ''


def getMusicRecommendationLDA(fileName, email, query, fileRatings, alreadyLiked):
    textCorpus = [query]  # Contiene una lista di generi per un utente
    artistdf = []

    with open(fileName, 'r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter=',')
        for row in reader:

            # Scarto la prima riga
            if 'artist_mb' in row[1]:
                continue

            if row[2]:
                pp_genre = row[2].split(';')
                pp_genre = pp.preprocess_string(row[2],
                                                CUSTOM_FILTERS)  # Faccio il pre-processing del genere dell'artista
                pp_genre.append(row[1])

                if len(pp_genre) > 2:
                    textCorpus.append(pp_genre)
                    artistdf.append(row)

    # Create a dictionary representation of the documents.
    dictionary = Dictionary(textCorpus)

    # Remove words that appear less than 5 times and that are in more than in 60% documents
    dictionary.filter_extremes(no_below=10, no_above=0.6)

    # Bag-of-words representation of the documents.
    dictionary.save('musica.dict')

    dictionary = dictionary.load('musica.dict')
    corpus = [dictionary.doc2bow(doc) for doc in textCorpus]

    # Train LDA Model
    # Set training parameters.
    num_topics = 100
    chunksize = 10
    passes = 20
    iterations = 400
    eval_every = None  # Don't evaluate model perplexity, takes too much time.

    NUM_PASSES = 10
    NUM_TOPICS = 100
    RANDOM_STATE = 1

    # Make a index to word dictionary.
    temp = dictionary[0]  # This is only to "load" the dictionary.
    id2word = dictionary.id2token

    '''
    lda = LdaModel(
        corpus=corpus,
        id2word=id2word,
        chunksize=chunksize,
        alpha='auto',
        eta='auto',
        iterations=iterations,
        num_topics=num_topics,
        passes=passes,
        eval_every=eval_every
    )'''

    lda = LdaModel(corpus, id2word=dictionary, random_state=RANDOM_STATE,num_topics=NUM_TOPICS, passes=NUM_PASSES)
    # corpusLDA = corpora.MmCorpus("corpus.mm")
    index = gensim.similarities.MatrixSimilarity(lda[corpus])
    index.save("simIndex.index")

    top_topics = lda.top_topics(corpus)  # num_words=20
    # print(top_topics)

    print(query)
    vec_bow = dictionary.doc2bow(query)

    vec_lda = lda[vec_bow]
    sims = index[vec_lda]

    for s in sorted(enumerate(sims), key=lambda item: -item[1])[:10]:

        if not (artistdf[s[0]][1].lower() in alreadyLiked):
            with io.open(fileRatings, "a", encoding="utf-8") as myfile:
                myfile.write(email + ";")
                myfile.write(artistdf[s[0]][1] + ";")
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

    # Lista contenente le preferenze positive dell'utente
    preference = []
    query = ""
    alreadyLiked = []

    # Itero attraverso la lista JSON
    for i in data['interests']:

        # Se abbiamo una preferenza positiva dell'utente per le news
        if i['source'] == 'music_preference' and 'Like:' in i['value'] and not ('Dislike:' in i['value']) \
                and ('Genre:' in i['value'] or 'Artist:' in i['value']):

            data = i['value'].replace('Like:', '').replace('Artist:', '').replace('Genre:', '')

            if 'Artist' in i['value']:
                alreadyLiked.append(data.lower())

            if len(data) > 2:
                preference.append(data)
                query += " " + data

    if len(query) > 10 and len(preference) >= 3:

        if Technique == 1:
            newPreference = ''
            for a in preference:
                a = a.replace(';', ' ')
                newPreference += a + ' '
            newPreference = newPreference.split(' ')

            getMusicRecommendationW2V('artistCleanOutput.csv', email, newPreference, "rec_music.csv", alreadyLiked)
        elif Technique == 2:
            newPreference = ''
            for a in preference:
                a = a.replace(';', ' ')
                newPreference += a + ' '
            newPreference = newPreference.split(' ')
            getMusicRecommendationFastText('artistCleanOutput.csv', email, newPreference, "rec_music.csv", alreadyLiked)
        elif Technique == 3:
            newPreference = ''
            for a in preference:
                a = a.replace(';', ' ')
                newPreference += a + ' '
            newPreference = newPreference.split(' ')

            getMusicRecommendationDoc2Vec('artistCleanOutput.csv', email, newPreference, "rec_music.csv", alreadyLiked)
        else:
            newPreference = ''
            for a in preference:
                a = a.replace(';', ' ')
                newPreference += a + ' '
            newPreference = newPreference.split(' ')

            getMusicRecommendationLsi('artistCleanOutput.csv', email, newPreference, "rec_music.csv", alreadyLiked)


def mainRun():
    Technique = 2
    try:
        f = open('rec_music.csv', 'r+')
        f.truncate(0)
    except:
        print("file to be created")
        f = open('rec_music.csv', 'w')
        f.close()

    # Lettura file degli utenti di Myrror
    for (dirpath, dirnames, filenames) in walk("fileMyrror"):
        for file in filenames:
            if file.startswith('past_'):
                email = file.split("past_", 1)[1]
                email = os.path.splitext(email)[0]

                profileBuilder(file, email, Technique)


# Utilizzo Word2Vec
# wv = api.load('word2vec-google-news-300')

# Utilizzo FastText
ft = load_facebook_model('fasttext/wiki.simple.bin')

# Utilizzo Doc2Vec
# dv = Doc2Vec.load("doc2vec_modelMusic")  # you can continue training with the loaded model!

mainRun()
