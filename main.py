import sys

import feedparser
import io
import time
from newspaper import Article
import threading
import csv
from datetime import datetime, timedelta
from bs4 import BeautifulSoup


categorieEn = [
    #'https://news.google.com/news/rss/headlines/section/topic/BUSINESS?hl=en-US&gl=US',
    #'https://news.google.com/news/rss/headlines/section/topic/TECHNOLOGY?hl=en-US&gl=US',

    #'https://news.google.com/news/rss/headlines/section/topic/WORLD?hl=en-US&gl=US',
    #'https://news.google.com/news/rss/headlines/section/topic/ENTERTAINMENT?hl=en-US&gl=US',

    #'https://news.google.com/news/rss/headlines/section/topic/SPORTS?hl=en-US&gl=US',
    #'https://news.google.com/news/rss/headlines/section/topic/SCIENCE?hl=en-US&gl=US',
    #'https://news.google.com/news/rss/headlines/section/topic/HEALTH?hl=en-US&gl=US',
    #'https://news.google.com/rss?hl=us-US&gl=US&ceid=US:en',
    #'http://xml2.corriereobjects.it/rss/english.xml',
    'https://www.ansa.it/english/english_rss.xml'
]

categorieIt = [
    #'https://news.google.com/news/rss/headlines/section/topic/BUSINESS?hl=it-IT&gl=IT',
    #'https://news.google.com/news/rss/headlines/section/topic/TECHNOLOGY?hl=it-IT&gl=IT',

    #'https://news.google.com/news/rss/headlines/section/topic/WORLD?hl=it-IT&gl=IT',
    #'https://news.google.com/news/rss/headlines/section/topic/ENTERTAINMENT?hl=it-IT&gl=IT',

    #'https://news.google.com/news/rss/headlines/section/topic/SPORTS?hl=it-IT&gl=IT',
    #'https://news.google.com/news/rss/headlines/section/topic/SCIENCE?hl=it-IT&gl=IT',
    #'https://news.google.com/news/rss/headlines/section/topic/HEALTH?hl=it-IT&gl=IT',
    #'https://news.google.com/rss?hl=it-IT&gl=IT&ceid=IT:it',
    #'http://xml2.corriereobjects.it/rss/homepage.xml',
    'https://www.ansa.it/sito/notizie/cultura/cultura_rss.xml'
]


# lan = 'it'/'en'
# fileName = "newsIta.csv"/"newsEn.csv"
def readFeedRss(categorie_lan, lan, fileName):
    categorie = categorie_lan

    now = datetime.now()

    i = 0
    for c in categorie:

        if i == 0:
            cat = "BUSINESS"
        elif i == 1:
            cat = "TECHNOLOGY"
        elif i == 2:
            cat = "WORLD"
        elif i == 3:
            cat = "ENTERTAINMENT"
        elif i == 4:
            cat = "SPORTS"
        elif i == 5:
            cat = "SCIENCE"
        elif i == 6:
            cat = "HEALTH"
        elif i == 7:
            cat = "ALL"

        feed = feedparser.parse(c)
        i = i + 1

        for entry in feed.entries:
            article_title = entry.title
            article_link = entry.link

            soup = BeautifulSoup(entry.description, features="lxml") # contenuto della notizia
            texts = soup.findAll(text=True)
            article_description = ' '.join(texts)

            try:
                article = Article(url=article_link, language=lan)
                article.download()
                article.parse()
                top_image = article.top_image
                image = top_image
            except:
                image = "null"

            if not checkFile(article_title, fileName):
                with io.open(fileName, "a", encoding="utf-8") as myfile:

                    if not (
                            ";" in article_link or ";" in image):  # se sono presenti i ; nei link e nelle immagini allora non scrivo la notizia
                        article_title = article_title.replace(';',
                                                              ' ')  # sostituisco il ; se presente nel titolo con uno spazio
                        myfile.write(article_title + ";")

                        myfile.write(article_link + ";")
                        myfile.write(image + ";")
                        myfile.write(cat + ";")
                        myfile.write(str(datetime.timestamp(now)) + ";")  # timestamp

                        article_description = article_description.replace(';', ',')
                        article_description = article_description.replace(' ', ' ')
                        myfile.write(article_description + "\n")


#Controlla i doppi inserimenti nel file
def checkFile(link, fileName):
    f = open(fileName, "r", encoding="utf8")
    count = 0
    while True:
        count += 1

        # Get next line from file
        line = f.readline()

        # if line is empty end of file is reached
        if not line:
            break
        arr = line.split(";")
        if arr[0] != '\n':
            # print("Line{}: {}".format(count, arr[1]))
            if arr[0] == link:
                return True
    return False


def runFeed(daysLimit):
    # creating thread
    t1 = threading.Thread(target=readFeedRss, args=(categorieIt, 'it', "newsIta.csv",))
    t2 = threading.Thread(target=readFeedRss, args=(categorieEn, 'en', "newsEn.csv",))

    # starting thread 1
    print("Feed ITA started!")
    t1.start()
    # starting thread 2
    print("Feed EN started!")
    t2.start()

    # wait until thread 1 is completely executed
    t1.join()
    # wait until thread 2 is completely executed
    t2.join()

    # both threads completely executed
    print("Feed ita/en completed!")

    # delete old news
    deleteNews("newsIta.csv", daysLimit)
    deleteNews("newsEn.csv", daysLimit)
    print('News meno recenti eliminate')


# Cancella le news meno recenti dal file csv
def deleteNews(fileName, daysLimit):
    now = datetime.now()

    # make a day limit
    datelimit = datetime.today() - timedelta(days=daysLimit)

    # list of news to delete
    newsRecent = list()

    # Prendo tutte le date più recenti presenti nel file
    with open(fileName, 'r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter=';')
        for row in reader:
            try:
                dt_object = datetime.fromtimestamp(float(row[4]))

                if dt_object >= datelimit:  # se la data nel file è più recente la salvo nella lista
                    newsRecent.append(row)
            except:
                print('')

    # Scrivo nel file solo quelle recenti
    with open(fileName, 'w+', encoding="utf-8", newline='') as result_file:
        wr = csv.writer(result_file, delimiter=';')
        wr.writerows(newsRecent)


try:
    timeReload = sys.argv[1]  # ore
    timeClean = sys.argv[2]  # giorni
except:
    timeReload = 12  # ore
    timeClean = 2  # giorni


WAIT_SECONDS = 2
ticker = threading.Event()
while not ticker.wait(WAIT_SECONDS):
    runFeed(timeClean)  # come argomento si imposta il limite di giorni per le news da eliminare
    WAIT_SECONDS = 60 * 60 * timeReload
