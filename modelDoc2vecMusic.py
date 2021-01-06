import csv

from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
import pandas as pd


# Convert list to string, by joining all item in list with given separator. Returns the concatenated string
def convert_list_to_string(org_list, seperator=' '):
    return seperator.join(org_list)


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

# Tagging documents. Each sentences(set of words) are mapped unique index.
# Tagged documents are input for doc2vec model.
tagged_documents = []
for i, doc in enumerate(genres):
    tagged = TaggedDocument(doc, [i])
    tagged_documents.append(tagged)

# Create new list of preference and vectorize it (preference of the user) ----> FRASE TEST
preferenceList = ['latin;reggaeton;trap latino;', 'bad bunny;', 'trap italiana;', 'fred de palma;',
                  'italian adult pop;italian pop;', 'fedez;', 'latin;reggaeton;reggaeton colombiano;', 'maluma;',
                  'latin;latin hip hop;reggaeton;trap latino;', 'ozuna;', 'dance pop;hip hop;miami hip hop;pop;',
                  'j balvin;', 'anuel aa;', 'latin;latin hip hop;reggaeton;reggaeton flow;', 'don omar;',
                  'latin;latin arena pop;latin pop;', 'luis fonsi;']



# Create doc2vec model and train it
#dv = Doc2Vec(tagged_documents, vector_size=100, window=2, min_count=10, workers=4, epochs=100)
#dv.train(tagged_documents, total_examples=dv.corpus_count, epochs=dv.epochs)

# Save the model and load it
#dv.save("doc2vec_modelMusic")
dv = Doc2Vec.load("doc2vec_modelMusic")  # you can continue training with the loaded model!

new_sentence = convert_list_to_string(preferenceList).split(";")
print(new_sentence)
new_sentence_vectorized = dv.infer_vector(new_sentence)

# Calculate cosine similarity
similar_sentences = dv.docvecs.most_similar(positive=[new_sentence_vectorized], topn=5)

# Output
output = []
for i, v in enumerate(similar_sentences):
    index = v[0]
    output.append([i + 1, genres[index], artist[index], v[1]])

df = pd.DataFrame(output, columns=["rank", "common_texts", "artist", "cosine_similarity"])
pd.set_option("display.max_rows", None, "display.max_columns", None)
# df.to_csv("outTest.csv", index=False)
print(df)
