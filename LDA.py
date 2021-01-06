import io
import os.path
import re
import tarfile
import logging
import smart_open
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
from gensim.models.doc2vec import Doc2Vec
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
import nltk
import numpy

nltk.download('all')

def getTopicForQuery (question):
    newsdf = []
    docs = []
    #docs.append(question)
    fileName = 'newsEn2.csv'
    with open(fileName, 'r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter=';')
        tokenizer = RegexpTokenizer(r'\w+')
        # create English stop words list
        en_stop = set(stopwords.words('english'))
        # Create p_stemmer of class PorterStemmer
        p_stemmer = nltk.stem.porter.PorterStemmer()
        for row in reader:

            if row[5] and len(row[5]) > 10:
                raw = row[5].lower()
                tokens = tokenizer.tokenize(raw)
                # remove stop words from tokens
                stopped_tokens = [i for i in tokens if not i in en_stop]
                # stem tokens
                stemmed_tokens = [p_stemmer.stem(i) for i in stopped_tokens]
                #stemmed_tokens = stopped_tokens
                docs.append(stemmed_tokens)
                newsdf.append(row)

    # Remove numbers, but not words that contain numbers.
    docs = [[token for token in doc if not token.isnumeric()] for doc in docs]

    # Remove words that are only one character.
    docs = [[token for token in doc if len(token) > 1] for doc in docs]

    # Lemmatize the documents.
    from nltk.stem.wordnet import WordNetLemmatizer

    lemmatizer = WordNetLemmatizer()
    docs = [[lemmatizer.lemmatize(token) for token in doc] for doc in docs]

    from gensim.corpora import Dictionary

    # Create a dictionary representation of the documents.
    dictionary = Dictionary(docs)

    # Filter out words that occur less than 20 documents, or more than 50% of the documents.
    dictionary.filter_extremes(no_below=2, no_above=0.5)
    # logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
    # Bag-of-words representation of the documents.
    dictionary.save('musica.dict')
    corpus = [dictionary.doc2bow(doc) for doc in docs]



    # Train LDA model.
    from gensim.models import LdaModel

    # Set training parameters.
    num_topics = 200
    chunksize = 50
    passes = 20
    iterations = 400
    eval_every = None  # Don't evaluate model perplexity, takes too much time.

    # Make a index to word dictionary.
    temp = dictionary[0]  # This is only to "load" the dictionary.
    id2word = dictionary.id2token

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
    )
    #corpusLDA = corpora.MmCorpus("corpus.mm")
    index = gensim.similarities.MatrixSimilarity(lda[corpus])
    index.save("simIndex.index")

    top_topics = lda.top_topics(corpus)  # , num_words=20)

    # Average topic coherence is the sum of topic coherences of all topics, divided by the number of topics.
    avg_topic_coherence = sum([t[1] for t in top_topics]) / num_topics
    print('Average topic coherence: %.4f.' % avg_topic_coherence)

    from pprint import pprint
    #pprint(top_topics)
    important_words = []
    temp = question.lower()

    tokens = tokenizer.tokenize(temp)
    # remove stop words from tokens
    stopped_tokens = [i for i in tokens if not i in en_stop]
    # stem tokens
    doc = [p_stemmer.stem(i) for i in stopped_tokens]


    important_words = [lemmatizer.lemmatize(token) for token in doc]
    print(important_words)



    dictionary = Dictionary.load('musica.dict')


    vec_bow = dictionary.doc2bow(important_words)
    vec_lda = lda[vec_bow]

    sims = index[vec_lda]

    for s in sorted(enumerate(sims), key=lambda item: -item[1])[:10]:
                print(s)
                print(newsdf[s[0]][1] + ";")
                print('{} \n'.format(s[1]))

    return ''
    #return question_topic[1]

query1= "Best soundbars with Amazon Alexa for 2021    CNET Alexa in 2021: Here's what to expect    " \
        "Tom's Guide Get a Google Nest Audio 2-pack for $150 ($48 off)    Android Police The best smart home devices for 2021: " \
        "Amazon, Google and Apple race to control your home    CNET The 7 best smart home devices I actually use on a daily basis   Tom's Guide" \
        "There are now three different models of Apple AirPods, and they can do a lot more than just play music "
query2 = "The presidential transition team laid out several priorities, such as revising who can make an asylum claim first and ending what they call artificial capacity limits that restrict how many immigrants can be processed at the border. View Entire Post Here’s What Is Changing After The FinCEN Files Shook The World Of Banking"

query3 = "Researchers Make Progress Toward High-Performing Water Desalination Membranes | Materials Science, Physical Chemistry    Sci-News.com" \
        "Future Zero-Emissions Power Plants: Scientists Collaborate on Development of Commercial Fusion Energy " \
        "   SciTechDaily Nuclear fusion group calls for building a pilot plant by the 2040s    The San Diego Union-Tribune"


query = "Steph Curry goes in depth on what went wrong for Warriors vs. the Nets | NBA on ESPN    ESPN Are We Sure the Brooklyn Nets Should Want James Harden?    Bleacher Report TNT crew roasts Kevin Durant for giving stiff interview    Yardbarker Kevin Durant returns in grand style as Brooklyn Nets open season with emphatic home win    ESPN Stephen Curry Joined NBA on TNT Ahead Of Opening Night | Full Interview    Bleacher Report"
getTopicForQuery(query1)