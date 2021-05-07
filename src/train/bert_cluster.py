import en_trf_bertbaseuncased_lg
import nltk
from nltk.cluster import KMeansClusterer
import pandas as pd
from typing import List
from src.util import get_keyword_window


def bert_en(select_word, sentences: List[str]):
    nlp = en_trf_bertbaseuncased_lg.load()
    sents_vectors = []
    for sent in sentences:
        words = sent.split(' ')
        sent2 = get_keyword_window(select_word, words, length=10)
        sent2 = ' '.join(sent2)
        sent_vect = nlp(sent2).vector
        sents_vectors.append(sent_vect)
    print(sents_vectors)
    return sents_vectors


def clustering_question(sents, sents_word2vec, NUM_CLUSTERS=15):
    kclusterer = KMeansClusterer(
        NUM_CLUSTERS, distance=nltk.cluster.util.cosine_distance,
        repeats=25, avoid_empty_clusters=True)

    assigned_clusters = kclusterer.cluster(sents_word2vec, assign_clusters=True)
    data = pd.DataFrame([], columns=['text', 'cluster', 'centroid'])
    data.loc[:, 'text'] = sents
    data.loc[:, 'cluster'] = pd.Series(assigned_clusters, index=data.index)
    data.loc[:, 'centroid'] = data['cluster'].apply(lambda x: kclusterer.means()[x])

    return data, assigned_clusters


if __name__ == "__main__":
    sents = ['In 222 BC, the Romans besieged Acerrae, an Insubre fortification on the right bank of the River Adda between Cremona and Laus Pompeia (Lodi Vecchio).',
             'A spokesman for the bank said "We will be compensating customers who did not receive full services from Affinion, and providing our apology."',
              'One of the first fully functional direct banks in the United States was the Security First Network Bank (SFNB), which was launched in October 1995, and was the first direct bank to be insured by the Federal Deposit Insurance Corporation.']
    sents_vectors = bert_en('bank', sents)
    clustering_question(sents, sents_vectors, 2)
