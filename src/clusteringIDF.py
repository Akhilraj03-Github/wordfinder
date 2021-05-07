import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.
import pprint
from nltk.corpus import stopwords

class Vectorization:

    def vectorize(self):

        documentA = 'the man went out for a walk'
        documentB = 'the children sat around the fire'

        bagOfWordsA = documentA.split(' ')
        bagOfWordsB = documentB.split(' ')

        uniqueWords = set(bagOfWordsA).union(set(bagOfWordsB))

        numOfWordsA = dict.fromkeys(uniqueWords, 0)

        for word in bagOfWordsA:
            numOfWordsA[word] += 1

        numOfWordsB = dict.fromkeys(uniqueWords, 0)

        for word in bagOfWordsB:
            numOfWordsB[word] += 1
        
        stopwords.words('english')

        tfA = self.computeTF(numOfWordsA, bagOfWordsA)
        tfB = self.computeTF(numOfWordsB, bagOfWordsB)


        idfs = self.computeIDF([numOfWordsA, numOfWordsB])


        tfidfA = self.computeTFIDF(tfA, idfs)
        tfidfB = self.computeTFIDF(tfB, idfs)

        df = pd.DataFrame([tfidfA, tfidfB])

        pprint.pprint(df)

    def computeTF(self, wordDict, bagOfWords):
        tfDict = {}
        bagOfWordsCount = len(bagOfWords)
        for word, count in wordDict.items():
            tfDict[word] = count / float(bagOfWordsCount)
        return tfDict

    def computeIDF(self, documents):
        import math
        N = len(documents)
    
        idfDict = dict.fromkeys(documents[0].keys(), 0)
        for document in documents:
            for word, val in document.items():
                if val > 0:
                    idfDict[word] += 1
    
        for word, val in idfDict.items():
            idfDict[word] = math.log(N / float(val))
        return idfDict
    

    def computeTFIDF(self, tfBagOfWords, idfs):
        tfidf = {}
        for word, val in tfBagOfWords.items():
            tfidf[word] = val * idfs[word]
        return tfidf

    def TFIDFUsingSkLearn(self):
        '''
            TFIDF 

            a  the      walk       sat       man       for    around      fire       out  children      went
        0  0.099021  0.0  0.099021  0.000000  0.099021  0.099021  0.000000  0.000000  0.099021  0.000000  0.099021
        1  0.000000  0.0  0.000000  0.115525  0.000000  0.000000  0.115525  0.115525  0.000000  0.115525  0.000000

        '''
        
        vectorizer = TfidfVectorizer()
        vectors = vectorizer.fit_transform([documentA, documentB])
        feature_names = vectorizer.get_feature_names()
        dense = vectors.todense()
        denselist = dense.tolist()
        df = pd.DataFrame(denselist, columns=feature_names)
        

if __name__ == '__main__':
    search = Vectorization()
    search.vectorize()
        
    
