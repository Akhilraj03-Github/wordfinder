# This module provides service functionality to app.py
# working directory is src folder.

import json
import sys
import os

import pandas as pd
import numpy as np
from typing import List
from sklearn.cluster import KMeans
from collections import defaultdict
import pymysql

from src.train.result_model import TResult
from src.train.store import StoreData
from src.util import (language_dict,
                      language_list,
                      db_config,
                      corpus_language,
                      udpipe_language,
                      get_keyword_window)
from src.train.train_cluster import load_model
from src.train.train_model import UdpipeTrain
from src.train.cluster import Evaluator
import re
from src.train.KWIC import keywords_in_context, find_and_replace
from src.util import get_keyword_window, kwic_show


try:
    store_data = StoreData(db_config['user'],
                           db_config['password'],
                           db_config['host'],
                           db_config['database'])
    cnx = store_data.db_connect()
    cursor = cnx.cursor()
except Exception as ex:
    print('logging in database error %s' % ex)

POS_COLUMN_INDEX, SENTENCE_COLUMN_INDEX = 2, 6


class AppService(object):
    def __init__(self):
        self.pos_dict = None
        self.sel_result = None
        self.udt_pre_model = None

    def config_udpipe(self, language_name):
        # first loading udpipe to segement word for each sentence
        # all these need to be at preprocessed level
        self.udt_pre_model = UdpipeTrain(language_name,
                                         udpipe_language[language_name],
                                         corpus_language[language_name])
        return self

    def find_service(self, language_name: str, sel_word: str):
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
            cursor.execute(sql_str, (sel_word,))
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
        self.sel_result = [(sel_word, k, self.pos_dict[k]) for k in self.pos_dict]

    def database(self):
        self.store_data = StoreData(db_config['user'],
                                    db_config['password'],
                                    db_config['host'],
                                    db_config['database'])
        self.cursor = self.store_data.db_connect().cursor()
        query_info = "SELECT sentence FROM english_sentences"
        self.cursor.execute(query_info)
        sentences_df = pd.DataFrame(self.cursor.fetchall(), columns=['Sentences'])
        return sentences_df

    def clusteringData(self):
        self.store_data = StoreData(db_config['user'],
                                    db_config['password'],
                                    db_config['host'],
                                    db_config['database'])
        self.cursor = self.store_data.db_connect().cursor()
        query_info = "SELECT sentence FROM english_sentences"
        self.cursor.execute(query_info)
        sentences_dataframe = pd.DataFrame(self.cursor.fetchall(), columns=['Sentences'])
        return sentences_dataframe

    def cluster_sentences(self, language_name: str, save_path: str, sentences: List[str], n_clusters: int) -> List[str]:
        """
        cluster sentences to get examples
        :param language_name:
        :param save_path: the saved path for our cluster udpipemodel trained well
        :param sentences:
        :param n_clusters:
        :return:
        """
        no_n_input = False
        if n_clusters == '':
            n_clusters, no_n_input = 2, True
        n_clusters = int(n_clusters)
        if n_clusters <= 0:
            print("Parameter is Invalid")
            return [None]*4
        if n_clusters > len(sentences):
            # TODO add log
            print('number of cluster bigger than sentences count')
            return [None]*4
        if len(self.sel_result) <= 0:
            print('no sentence')
            return [None]*4
        # first loading model
        # first loading udpipemodel
        word2vec_model = load_model(save_path)
        # second geting vectors for one sentence
        sent_vectors = []
        default_dimn = 100
        # iterator to sentence
        for sent in sentences:
            words = self.udt_pre_model.word_segmentation(sent)
            word_vectors = []
            # iterator to word
            window_words = get_keyword_window(self.sel_result[0][0], words, 5)
            for word in window_words:
                if word in word2vec_model.wv:
                    word_vectors.append(word2vec_model.wv[word])
                # else:  # not in dict, fill 0
                    # word_vectors.append([0] * default_dimn)

            to_array = np.array(word_vectors)
            sent_vectors.append(to_array.mean(axis=0).tolist())

        # third using kmeans to cluster
        best_score, best_labels = -1, None
        evaluator = Evaluator(sent_vectors)
        labels1 = evaluator.kmeans_strategy(n_clusters)
        score1 = evaluator.higher_better_score(labels1)
        labels2 = evaluator.agglomerative_strategy(n_clusters)
        score2 = evaluator.higher_better_score(labels2)
        if score1 < score2:
            best_score = score2
            best_labels = labels2
            print('agglomerative is better than kmeans')
        else:

            best_score = score1
            best_labels = labels1
            print('kmeans is better than agglomerative')

        labels3, n_clusters = evaluator.get_best_n_clusters()
        score3 = evaluator.higher_better_score(labels3)
        if best_score < score3:
            best_labels, best_score = labels3, score3

            best_score = score1
            best_labels = labels1
            print('kmeans is better than agglomerative')

        # fourth select one sentence with each label
        examples = self._get_examples(sentences, best_labels, n_clusters)

        labels3, recommend_clusters = evaluator.get_best_n_clusters()
        score3 = evaluator.higher_better_score(labels3)
        if best_score < score3:
            print('recommend %d sentences' % (recommend_clusters, ))
        recommend_sentences = self._get_examples(sentences, labels3, recommend_clusters)

        if no_n_input:
            examples = recommend_sentences

        return examples, recommend_sentences, sentences, best_labels

    def kwic(self, selword: str, sentence_with_pos: list):
        """
        :param: selword
        :param: sentenceWithPOS

        sentence_with_pos examples:
        [("NOUN", "bank", ["I go to the bank", "The house lies the right of the river bank"]),
        ("VERB", "bank", ["I banked in a slot"])
        """
        # This is similar to sentenceWithPOS but processed after KWIC
        result = []
        for sentTuple in sentence_with_pos:
            sents_kwic = []
            result.append((sentTuple[0], sentTuple[1], sentTuple[2], sents_kwic))

            sents_origin = sentTuple[2]
            for sent in sents_origin:
                # result_text = keywords_in_context(sent, [selword])
                # Highlight Keywords
                # result_text = find_and_replace(result_text, selword, "\x1b[34m" + selword + "\x1b[0m")
                # sents_kwic.append(result_text)
                window_words = get_keyword_window(selword, sent.split(" "))
                result_text = kwic_show(window_words, selword)
                if result_text:
                    print(result_text)
                    sents_kwic.append(result_text)

        return result

    def _get_examples(self, sentences: List[str], best_labels, n_clusters: int):
        tmp_labels, examples = [], []
        for sent, label in zip(sentences, best_labels):
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


class AppContext(object):
    sel_language = None
    sel_word = None
    sel_result_kwic = None


if __name__ == "__main__":
    '''
    # get word vector for one sentence
    language_name = 'English'
    sentences = [
        'Tohru shows great loyalty to whoever he stands by, even back to the time when he was an Enforcer for the Dark Hand.',
        'The Earth Demon, Dai Gui resembles a large minotaur(with the face of a guardian lion) with great strength.',
        'Al Mulock was the great-grandson of Sir William Mulock(1843–1944), the former Canadian Postmaster - General.',
        'Though his surviving images are scarce, his importance to the early history of photography in Asia is great.'
    ]
    save_path = './/corpus//english//'
    # first loading udpipe to segement word for each sentence
   
    udt_english = UdpipeTrain(language_list[1],
                              r'.//corpus//udpipemodel//english.udpipe',
                              r'.//corpus//english//135-0.txt')
    
    cluster_result = AppService().config_udpipe(language_name).cluster_sentences(language_name, save_path, sentences='3', n_clusters=2)
    '''
    cluster_result = AppService().config_udpipe(language_name).cluster_sentences(language_name, sentences, 2)
    print("two examples sentences: \n")
    print(cluster_result)
