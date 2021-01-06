import csv

from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
import pandas as pd
import gensim.parsing.preprocessing as pp

# pre-processing operations to apply
from nltk import word_tokenize

CUSTOM_FILTERS = [lambda x: x.lower(), pp.strip_tags,
                  pp.strip_punctuation,
                  pp.remove_stopwords,
                  pp.split_alphanum,
                  pp.strip_multiple_whitespaces]


# Convert list to string, by joining all item in list with given separator. Returns the concatenated string
def convert_list_to_string(org_list, seperator=' '):
    return seperator.join(org_list)


with open('newsEn.csv', 'r', encoding='utf-8') as file:
    reader = csv.reader(file, delimiter=';')

    links = []
    descriptions = []

    riga = []
    for row in reader:
        if row[5] and len(row[5]) > 10:
            pp_news = pp.preprocess_string(row[5],
                                           CUSTOM_FILTERS)  # Faccio il pre-processing della descrizione della notizia
            descriptions.append(pp_news)
            links.append(row[1])

file.close()

# Tagging documents. Each sentences(set of words) are mapped unique index.
# Tagged documents are input for doc2vec model.
tagged_documents = []
for i, doc in enumerate(descriptions):
    tagged = TaggedDocument(doc, [i])
    tagged_documents.append(tagged)

# Create new list of preference and vectorize it (preference of the user) ----> FRASE TEST
preferenceList = ['science', 'healty', 'nutrition', 'musk', 'covid', 'news', 'healty', 'vaccine',
                  'chemistry', 'spacex', 'mars', 'hyperloop', 'sun', 'cristiano ronaldo']

# Create doc2vec model and train it
dv = Doc2Vec(tagged_documents, vector_size=10, window=10, min_count=20, workers=16, epochs=90)
dv.train(tagged_documents, total_examples=dv.corpus_count, epochs=dv.epochs)

# Save the model and load it
dv.save("doc2vec_modelNews")
dv = Doc2Vec.load("doc2vec_modelNews")  # you can continue training with the loaded model!

new_sentence = convert_list_to_string(preferenceList).split(";")
print(new_sentence)
new_sentence_vectorized = dv.infer_vector(new_sentence)

# Calculate cosine similarity
similar_sentences = dv.docvecs.most_similar(positive=[new_sentence_vectorized], topn=5)

# Output
output = []
for i, v in enumerate(similar_sentences):
    index = v[0]
    output.append([i + 1, links[index], descriptions[index], v[1]])

df = pd.DataFrame(output, columns=["rank", "links", "tags", "cosine_similarity"])
pd.set_option("display.max_rows", None, "display.max_columns", None)
df.to_csv("outTest.csv", index=False)
print(df)
