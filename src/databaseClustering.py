import mysql.connector
from mysql.connector import errorcode
from datetime import datetime
import pandas as pd
import gensim.models
from typing import List
import numpy as np
from sklearn.cluster import KMeans
from nltk.tokenize import word_tokenize
import string
from util import db_config



def train_model(language_name, corpus_path, save_path):

	model = gensim.models.Word2Vec(sentences=corpus_path,
								   size=150,
								   window=8,
								   min_count=2,
								   workers=2,
								   iter=10)
	model.save(save_path + language_name)
	print('Save succeed')


def load_model(save_path) -> gensim.models.Word2Vec:
	filename = save_path
	model = gensim.models.Word2Vec.load(filename)
	print('Loading succeed')
	for index, word in enumerate(model.wv.index2word):
		if index == 5:
			break
		vec = ",".join(map(lambda i: str(i), model.wv[word]))
		print(f"word #{index}/{len(model.wv.index2word)} is {word}, vec = {vec}")
	return model

def database():

	db = mysql.connector.connect(
		host=db_config['host'],
		user=db_config['user'],
		password=db_config['password'],
		database=db_config['database']
		)
	mycursor = db.cursor()
	query_info = ("SELECT sentence FROM english_sentences")
	mycursor.execute(query_info)
	sentences_df= pd.DataFrame(mycursor.fetchall(), columns=['Sentences'])

	return sentences_df
	
def textProcessing(text):
    no_stop =[words for words in text.split() if words.lower() not in string.punctuation]
    return no_stop

def cluster_sentences(language_name: str, save_path: str, sentences: List[str], n_clusters: int) :

	n_clusters = int(n_clusters)
	print("clusters are ",n_clusters)
	if n_clusters <=0:
		print("Parameter is Invalid")
		return
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
	for word1 in sentences:
		print(word1)
		word_vectors = []
		for words in word1:
		
			if words in word2vec_model.wv:
				word_vectors.append(word2vec_model.wv[words])
			else:  # not in dict, fill 0
				word_vectors.append([0] * default_dimn)

	to_array = np.array(word_vectors)
	sent_vectors.append(to_array.mean(axis=0).tolist())
	kmeans = KMeans(n_clusters=n_clusters,random_state=0).fit(sent_vectors)
	labels = kmeans.labels_
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


a = database()
file_path = './corpus/word2vecmodel/'
language_name = 'english'
file_path = file_path + language_name
load_model(file_path)
print('All done')

c=a['Sentences'].apply(textProcessing)

# get word vector for one sentence
sentences = [
	'Tohru shows great loyalty to whoever he stands by, even back to the time when he was an Enforcer for the Dark Hand.',
	'The Earth Demon, Dai Gui resembles a large minotaur(with the face of a guardian lion) with great strength.',
	'Al Mulock was the great-grandson of Sir William Mulock(1843–1944), the former Canadian Postmaster - General.',
	'Though his surviving images are scarce, his importance to the early history of photography in Asia is great.']

cluster_result = cluster_sentences(language_name, file_path,c,3)
print("two examples sentences: \n")
print(cluster_result)

