# Recommender
Il file main.py crea i file newsIta e newsEn tramite i feed RSS, infine si occupa di chiamare
1)musicRecommender che crea le raccomandazioni per la musica
2)recsys crea le raccomandazioni per le notizie
Entrambi i recommender system producono 4 file di raccomandazione 1 per ogni tecnica implementata rispettivamente
1)w2v (WORD2VEC)
2)d2v (DOC2VEC)
3)ft (FASTTEXT)
4)lsi (LSA)

Nel caso delle news i file verranno generati sia per l'inglese che per l'italiano

Per avviarlo assicurarsi che alle'esterno della cartella Recommender ci sia la cartella fileMyrror generata da MyrrorBot.
Installare le seguenti librerie 
 pip install numpy scipy pandas sklearn lenskit gensim matplotlib feedparser 
 pip3 install newspaper3k
 
 
E' necessario scaricare i modelli pre-addestrati per word2vec fasttext e doc2vec:
E' possibile scaricare le librerie qui:
https://mega.nz/file/qUcnEarR#p-79IO4s98sRTTjerNxY2KGzh6MVZyOg35aHHQ9O224

Il file zip va estratto all'interno della cartella Recommender.

Per il deploy sul server:
  cd var/www/html/Recommender
  source virtualenvironment/project/bin/activate
  forever start -a -o ./out.log -e ./err.log -c python main.py
  
 
