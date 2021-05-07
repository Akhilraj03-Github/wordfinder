# This module mainly solve the cluster question
# to get example sentences.

import gensim.models
import tempfile
import argparse

from src.train.train_model import UdpipeTrain
from gensim.test.utils import datapath
from src.util import db_config
from src.util import language_list, db_config, corpus_language, udpipe_language


class ClusterModel(object):
    def __init__(self, corpus_language, udpipe_model: UdpipeTrain):
        self.corpus_path = corpus_language
        self.udpipe_model = udpipe_model
        self._word_count, self._MAX_WORD_COUNT = 0, 500000

    def __iter__(self):
        # corpus_path = datapath(self.filename)
        for line in open(self.corpus_path):
            # assume there's one document per line, tokens separated by whitespace
            # processed_line = utils.simple_preprocess(line)
            # processed_line = " ".join(processed_line)
            words = self.udpipe_model.word_segmentation(line)
            self._word_count += len(words)
            if self._word_count > self._MAX_WORD_COUNT:
                return
            print(words)
            yield words


def train_model(language_name,corpus_path,save_path,udpipe_model: UdpipeTrain):
    """
    train and save word2vec model
    def train_model(language_name, corpus_path, save_path, udpipe_model: UdpipeTrain):

    train and save word2vec udpipemodel
    :param udpipe_model:
    :param language_name:
    :param corpus_path: file path for train corpus
    :param save_path: vector udpipemodel path after finishing word2vec
    name rule of save_path is
    '/home/zglg/SLU/psd/cluster_pre_train/gensim-word2vec-udpipemodel-' + language_name
    :return:
    """

    sentences = ClusterModel(corpus_path, udpipe_model)
    model = gensim.models.Word2Vec(sentences=sentences,
                                   size=150,
                                   window=8,
                                   min_count=2,
                                   workers=2,
                                   iter=10)
    model.save(save_path + language_name)
    print('Save succeed')


def load_model(save_path) -> gensim.models.Word2Vec:
    """load udpipemodel we have trained
    :param save_path: filepath saved
    note: because we have ruled the name for word2vec udpipemodel, so rember to follow it.
    :return: word2vec udpipemodel we have trained
    """

    filename = save_path
    model = gensim.models.Word2Vec.load(filename)
    print('Loading succeed')
    # for index,word in enumerate(model.wv.index2word):
    #     if index == 5:
    #         break
    #     vec = ",".join(map(lambda i: str(i),model.wv[word]))
    #     print(f"word #{index}/{len(model.wv.index2word)} is {word}, vec = {vec}")
    return model


def batch():
    for lang in language_list:
        if lang in [
            'Chinese',
            'Dutch',
            'English',
            'Finnish',
            'French',
            'German',
            'Greek',
            'Hungarian',
            'Italian',
            'Japanese',
            'Korean',
            'Latin',
            'Polish',
            'Portuguese',
            'Russian',
            'Spanish'
        ]:
            continue
        udpipe_pre_model_path = udpipe_language[lang]
        corpus_filepath = corpus_language[lang]
if __name__ == "__main__":
    languange_name = 'English'

    # input example
    # # udpipe pre-train udpipemodel that we can download from a link in readme
    # udpipe_pre_model_path = '/home/zglg/SLU/psd/pre-udpipemodel/chinese-gsdsimp-ud-2.5-191206.udpipe'
    # # corpus for @language_name
    # corpus_filepath = '/home/zglg/SLU/psd/corpus/chinese/平凡的世界.txt'
    # # there are rules for word2vec file_path, please following:
    # file_path = '/home/zglg/SLU/psd/cluster_pre_train/gensim-word2vec-udpipemodel-'

    parser = argparse.ArgumentParser(description='train corpus to get our word2vec for multiple languages')
    parser.add_argument('-udfp', help='udpipe pre-udpipemodel filepath')
    parser.add_argument('-cfp', help='corpus filepath for a specific language')
    parser.add_argument('-wvfp', help='word vector filepath after finishing train')
    args = parser.parse_args()
    if 'udfp' in args:
        udpipe_pre_model_path = args.udfp
    else:
        print('please input udpipe pre-udpipemodel filepath')
    if 'cfp' in args:
        corpus_filepath = args.cfp
    else:
        print('please input corpus filepath')
    if 'wvfp' in args:
        file_path = args.wvfp
    else:
        print('please input word vector filepath')

    # first loading udpipe to segement word for each sentence
    udt_english = UdpipeTrain(languange_name, udpipe_pre_model_path, corpus_filepath)
    # second train to get the word2vec udpipemodel
    train_model(languange_name, corpus_filepath, file_path, udt_english)
    # finally, after train we can load udpipemodel to use directly
    load_model(file_path)
    print('All done')


    # first loading udpipe to segement word for each sentence
    # udt_lang = UdpipeTrain(lang, udpipe_pre_model_path, corpus_filepath)
    # second train to get the word2vec model
    # word2vec_result_file = 'corpus//word2vecmodel//gensim-word2vec-model-'
    # train_model(lang, corpus_filepath, word2vec_result_file, udt_lang)


if __name__ == "__main__":
    batch()
    # languange_name = 'English'
    #
    # # input example
    # # # udpipe pre-train model that we can download from a link in readme
    # # udpipe_pre_model_path = '/home/zglg/SLU/psd/pre-model/chinese-gsdsimp-ud-2.5-191206.udpipe'
    # # # corpus for @language_name
    # # corpus_filepath = '/home/zglg/SLU/psd/corpus/chinese/平凡的世界.txt'
    # # # there are rules for word2vec file_path, please following:
    # # file_path = '/home/zglg/SLU/psd/cluster_pre_train/gensim-word2vec-model-'
    #
    # parser = argparse.ArgumentParser(description='train corpus to get our word2vec for multiple languages')
    # parser.add_argument('-udfp', help='udpipe pre-model filepath')
    # parser.add_argument('-cfp', help='corpus filepath for a specific language')
    # parser.add_argument('-wvfp', help='word vector filepath after finishing train')
    # args = parser.parse_args()
    # if 'udfp' in args:
    #     udpipe_pre_model_path = args.udfp
    # else:
    #     print('please input udpipe pre-model filepath')
    # if 'cfp' in args:
    #     corpus_filepath = args.cfp
    # else:
    #     print('please input corpus filepath')
    # if 'wvfp' in args:
    #     file_path = args.wvfp
    # else:
    #     print('please input word vector filepath')
    #
    # # first loading udpipe to segement word for each sentence
    # udt_english = UdpipeTrain(languange_name, udpipe_pre_model_path, corpus_filepath)
    # # second train to get the word2vec model
    # train_model(languange_name, corpus_filepath, file_path, udpipe_pre_model_path)
    # # finally, after train we can load model to use directly
    # # load_model(file_path)
    # print('All done')
