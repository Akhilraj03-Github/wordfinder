"""
this module is mainly used to train our corpus according to UDpipe pre-train modules

Remember: working directory needed to be set to wordfinder!
"""


# third-party modules
import string
import re
import argparse

from corpy.udpipe import Model
from typing import List

from src.train.base_model import ITrain
from src.train.result_model import TResult
from src.train.store import StoreData
from src.util import language_list, db_config, corpus_language, udpipe_language


class UdpipeTrain(ITrain):
    def __init__(self, language_name, pre_model_name, our_corpus_name):
        """
        The language of pre_model_name and our_corpus_name should be identical!
        :param language_name:
        :param pre_model_name: it's from udpipe
        :param our_corpus_name: it's our found
        """
        self.language_name = language_name
        self.pre_model_name = pre_model_name
        self.our_corpus_name = our_corpus_name
        try:
            self.store_data = StoreData(db_config['user'],
                                        db_config['password'],
                                        db_config['host'],
                                        db_config['database'])
            self.cursor = self.store_data.db_connect().cursor()
            # second loading udpipe pre-train model
            self.model = Model(self.pre_model_name)
            self._word_count, self.MAX_WORD_COUNT = 0, 500000
            print('\n logging will start in database \n')
        except Exception as ex:
            print('logging in database error %s' % ex)

    def load_data(self) -> str:
        with open(self.our_corpus_name, 'r', encoding='utf-8') as f:
            for sent in f:
                print('loading one sentence: %s' % (sent,))
                yield sent

        print('loading done for our corpus')

    def clean_data(self, data: str) -> str:
        """
        data is one or several sentence(s) we expect
        if data is \n, \t, empty str, etc, replace them
        :param data: raw data
        :return: data after cleaning
        """
        cleaned_data = re.sub('\w*\d\w*', '', data)
        cleaned_data = re.sub('\[.*?\]', '', cleaned_data)
        cleaned_data = re.sub('[‘’“”…]','',cleaned_data)
        cleaned_data = re.sub(r'\\t | \\n', '', cleaned_data)
        return cleaned_data

    def do_train(self) -> List[TResult]:
        """
        By pre-train modules of unpipe get the results for our corpus
        These udpipe modules can be download here:
        https://lindat.mff.cuni.cz/repository/xmlui/handle/11234/1-3131
        :return:
        """
        # train our corpus to get POS for each word
        line_no = 1
        for sen in self.load_data():
            if self._word_count > self.MAX_WORD_COUNT:
                return
            sen_clean = self.clean_data(sen)
            if not sen_clean:
                continue
            word_pos = list(self.model.process(sen_clean))
            for i, one_sentence in enumerate(word_pos):
                sentence_text = self.extract_one_sentence(one_sentence)
                results = self.extract_one_word(one_sentence, sentence_text)
                self.store_data.insert_data(self.cursor, results, self.language_name)
                print('line %d, batch %d for %s written succeed' % (line_no, i, self.language_name))
            line_no += 1
        print(' all written succeed for corpus of %s' % self.our_corpus_name)

    def extract_one_sentence(self, sentence) -> str:
        """
       This private method is mainly used to extract the sentence text.
       an instance of udpipe Sentence:
       Sentence(
           comments=[
             '# sent_id = 3',
             '# text = 黄土高原严寒而漫长的冬天看来就要过去，但那真正温暖的春天还远远地没有到来。'],
           words=[
             Word(id=0, <root>),
             Word(id=1,
                  form='黄土',
                  lemma='黄土',
                  xpostag='NNP',
                  upostag='PROPN',
                  head=3,
                  deprel='nmod',
                  misc='SpaceAfter=No'),
             Word(id=2,
                  form='高原',
                  lemma='高原',
                  xpostag='NN',
                  upostag='NOUN',
                  head=3,
                  deprel='nmod',
                  misc='SpaceAfter=No')])
       :param sentence: udpipe Sentence
       :return: str 黄土高原
       """
        comment = ''.join(sentence.comments)
        try:
            single_sentence = re.findall(r'text = (.*)', comment)[0]
            return single_sentence
        except Exception as e:
            # TODO: need to write warning log
            print('error: not find a sentence', e)
            return ''

    def extract_one_word(self, sentence, sentence_text: str) -> [TResult]:
        """
        This private method is mainly used to extract one word and it's POS
        :param sentence_text:
        :param sentence:
        :return: [TResult]
        """
        combined_words = []
        for word in sentence.words:
            if word.lemma and word.lemma not in string.punctuation:
                if word.lemma and word.upostag and sentence_text:
                    combined_words .append(TResult(word.lemma, word.upostag, sentence_text))
                    self._word_count += 1
        return combined_words

    def word_segmentation(self, sentence) -> List[str]:
        """
        :param sentence:
        :return: word list
        """
        sen_clean = self.clean_data(sentence)
        if not sen_clean:
            return []
        word_pos = list(self.model.process(sen_clean))
        words = []
        for i, one_sentence in enumerate(word_pos):
            sentence_text = self.extract_one_sentence(one_sentence)
            results = self.extract_one_word(one_sentence, sentence_text)
            words.extend([res.word for res in results])
        return words


def batch_train():
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
        train_model = UdpipeTrain(lang, udpipe_pre_model_path, corpus_filepath)
        print('begin train %s corpus' % (lang, ))
        train_model.do_train()
        print('done train %s corpus' % (lang,))


if __name__ == '__main__':
    batch_train()
    parser = argparse.ArgumentParser(description='train corpus to get word, pos, and related sentence')
    parser.add_argument('-udfp', help='udpipe pre-model filepath')
    parser.add_argument('-cfp', help='corpus filepath for a specific language')
    args = parser.parse_args()
    if 'udfp' in args:
        udpipe_pre_model_path = args.udfp
    else:
        print('please input udpipe pre-model filepath')
    if 'cfp' in args:
        corpus_filepath = args.cfp
    else:
        print('please input corpus filepath')
    # Italian
    udt_chinese = UdpipeTrain(language_list[0], udpipe_pre_model_path, corpus_filepath)
    udt_chinese.do_train()
'''
# Chinese
udt_chinese = UdpipeTrain(language_list[0], udpipe_pre_model_path, corpus_filepath)
udt_chinese.do_train()

# Dutch
udt_dutch = UdpipeTrain(language_list[1], udpipe_pre_model_path, corpus_filepath)
udt_dutch.do_train()

# English
udt_english = UdpipeTrain(language_list[2], udpipe_pre_model_path, corpus_filepath)
udt_english.do_train()

# Finnish
udt_finnish = UdpipeTrain(language_list[3], udpipe_pre_model_path, corpus_filepath)
udt_finnish.do_train()

# French
udt_french = UdpipeTrain(language_list[4], udpipe_pre_model_path, corpus_filepath)
udt_french.do_train()

# German
udt_german = UdpipeTrain(language_list[5], udpipe_pre_model_path, corpus_filepath)
udt_german.do_train()

# Greek
udt_greek = UdpipeTrain(language_list[6], udpipe_pre_model_path, corpus_filepath)
udt_greek.do_train()

# Hungarian
udt_hungarian = UdpipeTrain(language_list[7], udpipe_pre_model_path, corpus_filepath)
udt_hungarian.do_train()

# Italian
udt_italian = UdpipeTrain(language_list[8], udpipe_pre_model_path, corpus_filepath)
udt_italian.do_train()

# Japanese
udt_japanese = UdpipeTrain(language_list[9], udpipe_pre_model_path, corpus_filepath)
udt_japanese.do_train()

# Korean
udt_korean = UdpipeTrain(language_list[10], udpipe_pre_model_path, corpus_filepath)
udt_korean.do_train()

# Latin
udt_latin = UdpipeTrain(language_list[11], udpipe_pre_model_path, corpus_filepath)
udt_latin.do_train()

# Polish
udt_polish = UdpipeTrain(language_list[12], udpipe_pre_model_path, corpus_filepath)
udt_polish.do_train()

# Portuguese
udt_portuguese = UdpipeTrain(language_list[13], udpipe_pre_model_path, corpus_filepath)
udt_portuguese.do_train()

# Russian
udt_russian = UdpipeTrain(language_list[14], udpipe_pre_model_path, corpus_filepath)
udt_russian.do_train()

# Spanish
udt_spanish = UdpipeTrain(language_list[15], udpipe_pre_model_path, corpus_filepath)
udt_spanish.do_train()
'''