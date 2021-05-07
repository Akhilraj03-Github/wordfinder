# this module is mainly used to be base class for train
# supporting the base interfaces for train udpipemodel.
# author: zhenguo
# date: 2021.2.26

from typing import List

from abc import ABCMeta, abstractmethod
from src.train.result_model import TResult


class ITrain(metaclass=ABCMeta):
    # when writing a word to database should filter udpipe <root> (udpipe.Word.lemma)
    # and these kinds of punctuations
    # BTW： maybe use regular expression
    # TODO: keep maintaining for this object
    # FILTER_WORD = ['<root>', ',', '，', '.', '。', ';', '；', '!', '！', '?', '？',
    #                '\\', '、', '“', '”', '……']

    @abstractmethod
    def load_data(self) -> str:
        """
        Due to the corpus file is possibly large, loading all to memory possibly
        causes memory overflow.

        Thus, it's more reasonable to load each sentence to
        memory one after one.
        :return: yield one sentence of inputing corpus
        """
        pass

    @abstractmethod
    def clean_data(self, data: str) -> str:
        """
        This method mainly cleans raw data, including:
        - delete stop word, if possible
        - delete unrelated text info, such as html labels, and
          finally only keep the text content we really want
        - others needed to do
        :param data: input raw text corpus
        :return: output corpus after cleaning
        """
        pass

    @abstractmethod
    def do_train(self) -> List[TResult]:
        """
        This method mainly does the train job, and train strategy is via udpipe
        or NLTK or other train strategies.

        About the train corpus, if it's very large, then loading memory possibly
        causes memory overflow. Thus, it's more reasonable to load each sentence to
        memory one after one.

        After loading one sentence with specific :param{language_name}, it's likely
        that calling self.clean_data method does the clean to this sentence. Then,
        by loading pre-train udpipemodel with specific :param{language_name}, we get each
        word and word's POS of this sentence.

        The result for this sentence would cache to TResult udpipemodel we define,
        then appennding a list. Finally, ruturn this list.

        :return: t
        """
        pass
