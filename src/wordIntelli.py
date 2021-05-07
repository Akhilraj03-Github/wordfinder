from nltk import tokenize
from nltk.tokenize import word_tokenize
import re, collections
import nltk, pysolr, stanfordcorenlp
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import wordnet as wn
from stanfordcorenlp import StanfordCoreNLP


from nltk import tokenize
from nltk.tokenize import word_tokenize
import re, collections
import nltk, pysolr, stanfordcorenlp
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import wordnet as wn
from stanfordcorenlp import StanfordCoreNLP

local_corenlp_path = r'C:/packages/nlp/stanford-corenlp-full-2017-06-09/'
server_corenlp_path = 'http://127.0.0.1'

class WordIntelli:
    def process_corpus(self, corpus):
        articles = corpus.read().split("\n\n")
        lst = []
        count = 0
        for article in articles:
            if article[0] == '#' and article[-1] == '#':
                continue
            else:
                count = count + 1
                tmp = "".join(article.split('\n'))
                tmp = "".join(article.split('\n'))
                lines = tokenize.sent_tokenize(tmp)
                for j in range(0, len(lines)):
                    print(['D', str(count), 'S', str(j+1)])
                    id = "".join(['D', str(count), 'S', str(j+1)])
                    lst.append(self.get_dictionary(lines[j], id))
        
        return lst

    '''Builds a dictionary'''
    '''D1S1 - id & @@176501 Either you 're flat or I am .'''

    def get_dictionary(self, line, id):
        tokens = word_tokenize(line)
        map = collections.OrderedDict()
        '''Build id '''
        map['id'] = id
        '''Tokenizing'''
        map['tokens'] = tokens
        '''POS Tagging'''
        tags = self.get_pos_tags(tokens)
        map['pos_tags'] = tags
        '''Lemmatize'''
        map['lemmas'] = self.get_lemmas(tokens, tags)
        '''Stemming'''
        map['stem_words'] = self.get_stems(tokens)
        '''Root words'''
        try:
            map['head_word'] = self.get_head_word(line)
        except:
            map['head_words'] = ''
        '''hypernyms'''
        map['hypernyms'] = self.get_hypernyms(tokens)
        '''hyponyms'''
        map['hyponyms'] = self.get_hyponyms(tokens)
        '''meronyms'''
        map['meronyms'] = self.get_meronyms(tokens)
        '''meronyms'''
        map['holonyms'] = self.get_holonyms(tokens)
        ''''''
        return map

    '''Splits sentence, Lemmatizes, merges and returns'''

    def get_pos_tags(self, tokens):
        # text = word_tokenize(line)
        tagged_tokens = nltk.pos_tag(tokens)
        tags = [x[1] for x in tagged_tokens]
        return tags #" ".join(tags).strip()

    def get_stems(self, tokens):
        # from nltk.stem.lancaster import LancasterStemmer
        from nltk.stem.porter import PorterStemmer
        ls = PorterStemmer()
        # text = word_tokenize(line)
        stem_words = [ls.stem(word) for word in tokens]
        return stem_words # " ".join(stem_words).strip()

    def get_hypernyms(self, tokens):
        # tokens = word_tokenize(line)
        hypernyms = []
        for token in tokens:
            syns = wn.synsets(token)
            if len(syns) > 0 and len(syns[0].hypernyms()) > 0:
                hns = syns[0].hypernyms()[0]
                hypernyms.append(hns.lemmas()[0].name())
            else:
                hypernyms.append(token)
        return hypernyms # " ".join(hypernyms).strip()

    def get_hyponyms(self, tokens):
        # tokens = word_tokenize(line)
        hyponyms = []
        for token in tokens:
            syns = wn.synsets(token)
            if len(syns) > 0 and len(syns[0].hyponyms()) > 0:
                hns = syns[0].hyponyms()[0]
                hyponyms.append(hns.lemmas()[0].name())
            else:
                hyponyms.append(token)
        return hyponyms

    def get_meronyms(self, tokens):
        # tokens = word_tokenize(line)
        meronyms = []
        '''Other meronyms available are substance_meronyms, member_meronyms'''
        for token in tokens:
            synsets = wn.synsets(token)
            if len(synsets) > 0 and (len(synsets[0].part_meronyms()) > 0 or len(synsets[0].member_meronyms()) > 0) :
                if len(synsets[0].part_meronyms()) > 0: # syns[0]
                    hns = synsets[0].part_meronyms()[0]
                else:
                    hns = synsets[0].member_meronyms()[0]
                meronyms.append(hns.lemmas()[0].name())
            else:
                meronyms.append(token)
        return meronyms

    def get_holonyms(self, tokens):
        # tokens = word_tokenize(line)
        holonyms = []
        '''Other meronyms available are substance_meronyms, member_meronyms'''
        for token in tokens:
            synsets = wn.synsets(token)
            if len(synsets) > 0 and (len(synsets[0].part_holonyms()) > 0 or len(synsets[0].member_holonyms()) > 0) :
                if len(synsets[0].part_holonyms()) > 0: # syns[0]
                    hns = synsets[0].part_holonyms()[0]
                else:
                    hns = synsets[0].member_holonyms()[0]
                holonyms.append(hns.lemmas()[0].name())
            else:
                holonyms.append(token)
        return holonyms #" ".join(holonyms).strip()


    def get_lemmas(self, tokens, pos_tags):
        # tags = word_tokenize(pos_tags)
        # text = word_tokenize(line)
        wnl = WordNetLemmatizer()
        lemmas = []
        for i in range(0, len(tokens)):
            tag = self.get_wordnet_pos(pos_tags[i])
            if tag != '':
                lemmas.append(str(wnl.lemmatize(tokens[i], tag)))
            else:
                lemmas.append(str(wnl.lemmatize(tokens[i])))
        return lemmas # " ".join(lst).strip() # return

    '''Adds JSON object to Solr core'''
    def add_fields(self, data, core):
        print("connecting to Solr.....")
        solr = pysolr.Solr('http://localhost:8983/solr/'+core,always_commit=True)
        solr.delete(q='*:*') #deletes existing fields and data from solr
        print('Indexing...')
        solr.add(data ) # indexes data into the core specified
        print('Completed indexing')

    def get_head_word(self, line):
        # https://github.com/Lynten/stanford-corenlp
        # nlp = StanfordCoreNLP(local_corenlp_path) # standalone method, with jar files downloaded locally
        nlp = StanfordCoreNLP(server_corenlp_path, port=9000) # with a working internet connection
        dep_parse = nlp.dependency_parse(line)
        ''' sentence = 'workers dumped sacks into a bin'
        0 workers 1 dumped 2 sacks 3 into 4 a 5 bin 6
        Dependency Parsing:
        [(u'ROOT', 0, 2), (u'nsubj', 2, 1), (u'dobj', 2, 3), (u'case', 6, 4), (u'det', 6, 5), (u'nmod', 2, 6)]
        head word: dumped # ROOT
        '''
        text = word_tokenize(line)
        head = ''
        if len(dep_parse[0]) > 2 and dep_parse[0][0] == u'ROOT' and len(text) > 0:
            head = text[dep_parse[0][2]-1]
        return head

    def query_solr(self, input, core):
        solr = pysolr.Solr('http://localhost:8983/solr/' + core)
        query = self.process_query(input)

        results = solr.search(q=query, sort='score desc', fl='score, id, tokens')

        print("Top 10 documents that closely match the query")
        i = 1
        print("No Document   Score Content")
        for result in results:
            sentence = ' '.join([str(r) for r in result['tokens']])
            print(str(i) + "\t" + result['id']+ "\t" + str(result['score']) + "\t" + sentence)
            i = i + 1

    def process_query(self, query):
        tokens = word_tokenize(query)
        tags = self.get_pos_tags(tokens)
        lemmas = self.get_lemmas(tokens, tags)
        stems = self.get_stems(tokens)
        head_word = self.get_head_word(query)# query: non-tokenized input
        hypernyms = self.get_hypernyms(tokens)
        hyponyms = self.get_hyponyms(tokens)
        meronyms = self.get_meronyms(tokens)
        holonyms = self.get_holonyms(tokens)
        query = "tokens: " + "||".join(tokens)
        query = query + " pos_tags:" + "||".join(tags)
        query = query + " lemmas: " + "||".join(lemmas)
        query = query + " stem_words: " + "||".join(stems)
        query = query + " head_word:" + head_word
        query = query + " hypernyms: " + "||".join(hypernyms)
        query = query + " hyponyms: " + "||".join(hyponyms)
        query = query + " meronyms: " + "||".join(meronyms)
        query = query + " holonyms: " + "||".join(holonyms)

        print(query)
        return query

    def get_wordnet_pos(self, treebank_tag):
        if treebank_tag.startswith('J'):
            return wn.ADJ
        elif treebank_tag.startswith('V'):
            return wn.VERB
        elif treebank_tag.startswith('N'):
            return wn.NOUN
        elif treebank_tag.startswith('R'):
            return wn.ADV
        else:
            return ''

if __name__ == '__main__':
    corpus = open('brownTest.txt')
    user_choice = input('Enter 1 to index, 2 to query\n')
    search = WordIntelli()
    if int(user_choice) == 1:
        data = search.process_corpus(corpus)
        print(data)
        search.add_fields(data, 'task3')#TODO: add port through cmd
    elif int(user_choice) == 2: #query
        input = input("Enter your query\n")
        search.query_solr(input, 'task3')
    

