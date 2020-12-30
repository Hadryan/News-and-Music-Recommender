import pandas as pd

'''
df = pd.read_csv('artists.csv',
                 dtype={"mbid": "string", "artist_mb": "string", "artist_lastfm": "string", "country_mb": "string"
                     , "country_lastfm": "string", "tags_mb": "string", "tags_lastfm": "string"})

# Rimozione duplicati
df = df.drop_duplicates(subset="artist_mb", keep="first")  # rimuovo i duplicati
df = df.drop_duplicates(subset="artist_lastfm", keep="first")  # rimuovo i duplicati

# Elimino le colonne
df = df.drop('country_mb', 1)
df = df.drop('country_lastfm', 1)
df = df.drop('listeners_lastfm', 1)
df = df.drop('scrobbles_lastfm', 1)
df = df.drop('ambiguous_artist', 1)

# Creo il file csv
df.to_csv('artistMiddle.csv', index=False)
'''

# Leggo dal file csv
df = pd.read_csv('artistMiddle.csv',
                 dtype={"mbid": "string", "artist_mb": "string", "artist_lastfm": "string", "tags_mb": "string", "tags_lastfm": "string"})

# Controllo artista e genere
i = 0
for index, row in df.iterrows():

    # Controllo artista
    if pd.isnull(row['artist_mb']):
        if not pd.isnull(row['artist_lastfm']):
            row['artist_mb'] = row['artist_lastfm']
        else:
            df.drop(index, inplace=True)  # elimino intera riga

    # Controllo il genere
    if pd.isnull(row['tags_mb']):
        if not pd.isnull(row['tags_lastfm']):
            row['tags_mb'] = row['tags_lastfm']
        else:
            df.drop(index, inplace=True)  # elimino intera riga

    i = i + 1
    print(i)



# Elimino le colonne
df = df.drop('artist_lastfm', 1)
df = df.drop('tags_lastfm', 1)


# Crea il csv
df.to_csv('artistCleanOutput.csv', index=False)
