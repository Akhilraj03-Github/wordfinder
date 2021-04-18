# This module provides service functionality to app.py
# working directory is src folder.

import json
import sys
import os

import numpy as np
from typing import List
from sklearn.cluster import KMeans
from collections import defaultdict

from src.train.result_model import TResult
from src.train.store import StoreData
from src.util import language_dict,language_list,db_config
from src.train.train_cluster import load_model
from src.train.train_model import UdpipeTrain

try:
    store_data = StoreData(db_config['user'],
                           db_config['password'],
                           db_host=db_config['db_host'],
                           db_name=db_config['db_name'])
    cnx = store_data.db_connect()
    cursor = cnx.cursor()
except Exception as ex:
    print('logging in database error %s' % ex)

POS_COLUMN_INDEX,SENTENCE_COLUMN_INDEX = 2,6


class AppService(object):
    def __init__(self):
        self.pos_dict = None
        self.sel_result = None
        self.udt_pre_model = None

    def config_udpipe(self,language_name):
        # first loading udpipe to segement word for each sentence
        # TODO: once getting language_name, then to find the related udpipe and corpus
        # all these need to be at preprocessed level
        self.udt_pre_model = UdpipeTrain(language_name,
                                         r'C:\Users\haris\Desktop\wordFinder\english-ewt-ud-2.5-191206.udpipe',
                                         r'C:\Users\haris\Desktop\wordFinder\haris.txt')
        return self

    def find_service(self,language_name: str,sel_word: str):
        """This method get results from database by specified language_name and input word
        assgin value to self.pos_dict and self.sel_result
        :param language_name:
        :param sel_word:
        :return: None
        """
        # select
        sql_str = "select * from " + language_name + "_wordpos as w left join " + language_name + "_sentences as s on " \
                                                                                                  "w.sentence = s.id " \
                                                                                                  "where w.word = %s "
        try:
            cursor.execute(sql_str,(sel_word,))
            self.sel_result = cursor.fetchall()
            cnx.commit()
        except Exception as e:
            print(e)

        # convert to data structure following
        # sel_result = (("sink", "NOUN", ["Don't just leave your dirty plates in the sink!"]),
        #                ("sink", "VERB", ["The wheels, started to sink into the mud.", "How could you sink so low?"]))
        self.pos_dict = defaultdict(list)
        for row in self.sel_result:
            pos_sentences = self.pos_dict[row[POS_COLUMN_INDEX]]
            if row[SENTENCE_COLUMN_INDEX] not in pos_sentences:
                pos_sentences.append(row[SENTENCE_COLUMN_INDEX])
        self.sel_result = [(sel_word,k,self.pos_dict[k]) for k in self.pos_dict]

    def cluster_sentences(self,language_name: str,save_path: str,sentences: List[str],n_clusters: int) -> List[str]:
        """
        cluster sentences to get examples
        :param language_name:
        :param save_path: the saved path for our cluster model trained well
        :param sentences:
        :param n_clusters:
        :return:
        """
        n_clusters = int(n_clusters)
        if n_clusters > len(sentences):
            # TODO add log
            print('number of cluster bigger than sentences count')
            return
        # first loading model
        word2vec_model = load_model(save_path)
        # second geting vectors for one sentence
        sent_vectors = []
        default_dimn = 100
        # iterator to sentence
        for sent in sentences:
            words = self.udt_pre_model.word_segmentation(sent)
            word_vectors = []
            # iterator to word
            for word in words:
                if word in word2vec_model.wv:
                    word_vectors.append(word2vec_model.wv[word])
                else:  # not in dict, fill 0
                    word_vectors.append([0] * default_dimn)

            to_array = np.array(word_vectors)
            sent_vectors.append(to_array.mean(axis=0).tolist())

        # third using kmeans to cluster
        kmeans = KMeans(n_clusters=n_clusters,random_state=0).fit(sent_vectors)
        labels = kmeans.labels_
        # fourth select one sentence with each label
        tmp_labels,examples = [],[]
        for sent,label in zip(sentences,labels):
            if label not in tmp_labels:
                tmp_labels.append(label)
                examples.append(sent)
            if len(examples) == n_clusters:
                break
        # add bottom logic for cluster
        if len(examples) < n_clusters:
            for sent in sentences:
                if sent not in examples:
                    examples.append(sent)
                if len(examples) >= n_clusters:
                    break

        return examples


if __name__ == "__main__":
    # get word vector for one sentence
    language_name = 'English'
    sentences = [
        'Tohru shows great loyalty to whoever he stands by, even back to the time when he was an Enforcer for the Dark Hand.',
        'The Earth Demon, Dai Gui resembles a large minotaur(with the face of a guardian lion) with great strength.',
        'Al Mulock was the great-grandson of Sir William Mulock(1843–1944), the former Canadian Postmaster - General.',
        'Though his surviving images are scarce, his importance to the early history of photography in Asia is great.']

    # first loading udpipe to segement word for each sentence
    udt_english = UdpipeTrain(language_list[1],
                              r'C:\Users\haris\Desktop\wordFinder\english-ewt-ud-2.5-191206.udpipe',
                              r'C:\Users\haris\Desktop\wordFinder\haris.txt')

    cluster_result = AppService().config_udpipe(language_name).cluster_sentences(language_name,sentences,2)
    print("two examples sentences: \n")
    print(cluster_result)
