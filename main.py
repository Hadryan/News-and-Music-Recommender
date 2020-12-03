import feedparser
import io
import sched
import time
from newspaper import Article
import threading

categorieEn = [
    'https://news.google.com/news/rss/headlines/section/topic/BUSINESS?hl=en-US&gl=US',
    'https://news.google.com/news/rss/headlines/section/topic/TECHNOLOGY?hl=en-US&gl=US',

    'https://news.google.com/news/rss/headlines/section/topic/WORLD?hl=en-US&gl=US',
    'https://news.google.com/news/rss/headlines/section/topic/ENTERTAINMENT?hl=en-US&gl=US',

    'https://news.google.com/news/rss/headlines/section/topic/SPORTS?hl=en-US&gl=US',
    'https://news.google.com/news/rss/headlines/section/topic/SCIENCE?hl=en-US&gl=US',
    'https://news.google.com/news/rss/headlines/section/topic/HEALTH?hl=en-US&gl=US',
    'https://news.google.com/rss?hl=us-US&gl=IT&ceid=US:en'
]

categorieIt = [
    'https://news.google.com/news/rss/headlines/section/topic/BUSINESS?hl=it-IT&gl=IT',
    'https://news.google.com/news/rss/headlines/section/topic/TECHNOLOGY?hl=it-IT&gl=IT',

    'https://news.google.com/news/rss/headlines/section/topic/WORLD?hl=it-IT&gl=IT',
    'https://news.google.com/news/rss/headlines/section/topic/ENTERTAINMENT?hl=it-IT&gl=IT',

    'https://news.google.com/news/rss/headlines/section/topic/SPORTS?hl=it-IT&gl=IT',
    'https://news.google.com/news/rss/headlines/section/topic/SCIENCE?hl=it-IT&gl=IT',
    'https://news.google.com/news/rss/headlines/section/topic/HEALTH?hl=it-IT&gl=IT',
    'https://news.google.com/rss?hl=it-IT&gl=IT&ceid=IT:it'
]


# lan = 'it'/'en'
# fileName = "newsIta.csv"/"newsEn.csv"
def readFeedRss(categorie_lan, lan, fileName):
    categorie = categorie_lan

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

            try:
                article = Article(url=article_link, language=lan)
                article.download()
                article.parse()
                top_image = article.top_image
                image = top_image
            except:
                image = ""

            if not checkFile(article_title, fileName):
                with io.open(fileName, "a", encoding="utf-8") as myfile:
                    myfile.write(article_title + ";")
                    myfile.write(article_link + ";")
                    myfile.write(image + ";")
                    myfile.write(cat + "\n")


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


def runFeed():
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
    print("Done!")


WAIT_SECONDS = 30
ticker = threading.Event()
while not ticker.wait(WAIT_SECONDS):
    runFeed()
    WAIT_SECONDS = 60*60*12
