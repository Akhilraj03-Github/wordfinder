# wordfinder

## 1 clone this repository

git clone git@git.cs.slu.edu:psd-project/wordfinder.git

If prompts you permission denied or enter your password or whatever, then you should follow this:

https://stackoverflow.com/questions/2643502/how-to-solve-permission-denied-publickey-error-when-using-git

last step you need to put your local "id_rsa. pub" file content to your "SSH keys" where it is in your gitlab Settings(top-right corner) and then you would see it left side: SSH keys.


By the way if you had any problem, please feel for free to contact me. 


Also, you can git clone https://oauth2:pZkqPY8oKTrx5KNCU8vy@git.cs.slu.edu/psd-project/wordfinder.git

but it's not the recommended way.

## Get Started

Current level we have a demo version following: 

First, select English language

Second, enter the word: sink, then click "Find" button

Enjoy the demo! Only support to show.

## 2 product backlog 

### 2.1 main functions of product

what's the main functionality of our product?
1.  support multilingualism
2.  enter a word and word's Part-Of-Speech, return corresponding sentences as fast as possible
3. Should then “cluster” those sentences into examples with related senses; Present to the user one or more “clusters” of example sentences
4. Must allow the user to examine, then change the number of clusters

### 2.2 Three main modules of big task

1. Database: gather and store text corpora in many languages in a way that makes queries of the type we want (word/part-of-speech lookup) fast and easy
2. Analysis: code to cluster example sentences containing given word; interesting machine learning approaches here that I’ll explain eventually!
3. Front end: simple, usable interface; must work on any platform, and should support messages/menu items in multiple languages

## 3 Sprint backlog

### 3.1 alpha version

what's the main functionality of the alpha version (deadline March 19)?
1. support at least two languages
2. finish design of database tables , including: word-tag-sentence table as language type, such as English table:

| word_name | pos_tag |                                        sentence |
| :-------- | :-----: | ----------------------------------------------: |
| sink      |  NOUN   | Don't just leave your dirty plates in the sink! |
| sink      |  VERB   |        The wheels started to sink into the mud. |
| sink      |  VERB   |                      How could you sink so low? |

3. Also, as fields above, we should train data and get tags of each word in our selected corpus and then put results to write into tables such as table called English_data, another table called Chinese_data, etc.

4. finish front-end disign, including available to any platform, supporting to enter word text box and supporting to  select messages/menu items in multiple languages, etc.

5. a simple alogrithm to implement “cluster” functionality: sentences found by search into examples with related senses.

6. support users to change the number of clusters. 

**Tips:**
- in alpha version we don't need to care to much about the number of words and maybe one millon words are OK, but need to support at least two language  
- Note a possible little trick: **sort** table accordig to alphabeta order.

- Preference choices for sql database is mysql

- NOTE We only return the sentences that **exactly** contain searched word, such as sink rather than sunk and sinking, etc.

- universal dependencies POS tag types: 

  - [ADJ](https://universaldependencies.org/u/pos/ADJ.html): adjective
  - [ADP](https://universaldependencies.org/u/pos/ADP.html): adposition
  - [ADV](https://universaldependencies.org/u/pos/ADV.html): adverb
  - [AUX](https://universaldependencies.org/u/pos/AUX_.html): auxiliary
  - [CCONJ](https://universaldependencies.org/u/pos/CCONJ.html): coordinating conjunction
  - [DET](https://universaldependencies.org/u/pos/DET.html): determiner
  - [INTJ](https://universaldependencies.org/u/pos/INTJ.html): interjection
  - [NOUN](https://universaldependencies.org/u/pos/NOUN.html): noun
  - [NUM](https://universaldependencies.org/u/pos/NUM.html): numeral
  - [PART](https://universaldependencies.org/u/pos/PART.html): particle
  - [PRON](https://universaldependencies.org/u/pos/PRON.html): pronoun
  - [PROPN](https://universaldependencies.org/u/pos/PROPN.html): proper noun
  - [PUNCT](https://universaldependencies.org/u/pos/PUNCT.html): punctuation
  - [SCONJ](https://universaldependencies.org/u/pos/SCONJ.html): subordinating conjunction
  - [SYM](https://universaldependencies.org/u/pos/SYM.html): symbol
  - [VERB](https://universaldependencies.org/u/pos/VERB.html): verb
  - [X](https://universaldependencies.org/u/pos/X.html): other

- more important and useful links about how we develop this project have put at [tmp](./tmp) folder


### 3.2 beta version

what's the main function of the beta version (deadline April 9 )?

to do

### 3.3 final version

what's the main function of the final version (deadline )?

to do

## development tools

tips:
- based on Dr.Scannell materials that contains important corpus we need, like UD
, and tools for POS tag like UDpipe. Once we build some codes, then we can write data to our tables of database, which is very important.

- Python as development language and  web application 
- our repository: https://git.cs.slu.edu/psd-project/wordfinder/-/project_members
- flask as the web framework as convenient 
- unit test 

## how assign to individual of group


## TODO list

HERE we make development plans, dicuss them and pass them. Then we should followthese plans to start. If happing a problem in development, you should tell us in time and then we group should sovle it together before deadline.

2/16/2021 - 2/21/2021 TASKS

# sprint 1: planning

1. Develop UI in any language 
2. Obtain Corpus 
3. Clean the Corpus(Tokenization, lemmatization and stemming)
4. Tag the data according the POS


### -------------------------------------------------
# sprint 2: planning

Discussion list:

1. discuss NLTK and UDpipe, key is multiple language support

2. corpus for 7-8 languages need to decide

  3 load UDpipe pre-train model, then train our corpus of 2

  4 let result write to our database, and core fields: word , POS tag,  sentence

  5  cluster sentences to get example sentences.

![big task steps](assets/big-task-1.png)


### Done list:
 User interface
 English corpora
 POS Tag

### To do list:
 Decide NLTK or CorPy
 Multilingual functionality 
 Start writing to csv to build database structure

### mysql

### view all tables of a database, here called mysql database

select table_name from information_schema.tables where table_schema='mysql';


# sprint 2: review

new features:

1. finish development of POS tag, based on udpipe pre-train model, available to multiple languages, including:
  - base_model.py
  - train_model.py
  - base data structure: result_model.py

2. finish application for database at hopper.slu.edu, which hosts our web servers and database store. Our train can be put on this server to keep running all time.

3. finish development for mysql store model, and the module is store.py 


unfinished features:

1. corpus for many other languages
2. cluster 

### -------------------------------------------------
# sprint 3: planning
- 1 methods to get corpus for many languages
    - 1.1 wikipedia : language abbreviation: https://zh.wikipedia.org/wiki/ISO_639-1
    - 1.2 how to get via wikipedia https://jdhao.github.io/2019/01/10/two_chinese_corpus/
      
2. database, tables structures
    - current tables structure
    - wordpos table and sentence table
    
    updating and cleaning the database all the time
    
3. add cluster function by word2vec 
   the gensim library can do it @Zhen Guo

4. on web interfaces we should add the show for cluster task @Zhen Guo

5. add logging for every key step

6. test task, cleaning the database @Willie @Haris 

7. deploy to hopper.slu.edu

8. alpha version release

### before beta version

Right now I found our repository has a problem considerable us to pay enough attention. Everyone has an individual file path and they are different from each other, 

such as file path of train corpus, the file path of cluster model, the file path of database config. These file paths cannot be pushed to our base repository! 

We should think of a nice way to solve this issue. And I have an idea. We should maintain a common file relative path and all data files and config data should be put inside it. Also, there's another important thing to remember: don't
push these corpus and pre-train models to our base repository. We should maintain a common remote disk to store and then open and share a link to provide everyone in our group to use.

I have created a file named input, there are three files inside it: corpus, udpipemodel, and word2vecmodel. All files in them are hosted at 

download: https://pan.baidu.com/s/14RzwuGjTZwsUhiyVSe-Pgg 
password: td3e

downloading them and put them on root directory of wordfiner folder


### sprint 5

1、database: we should build a remote DB @Willie
2、word2vec: two methods of doing that @Zhen 
3、we should label every sentence and show all sentences with a label to the cluster web interfaces @all


### -------------------------------------------------
# sprint 4: planning

review codes we have pushed to the base github repo @all
with models we had train more languages, train_model. py to database, cluster_model. py to get word2vec model(it doesn't need to store database so everyone can do it)@all
test every py module and welcome to commit bugs we everyone find @all
with logging module add logs before and after important events @all
Time complexity for this task is a needed issue for us to consider.

1. DATABASE
    1. create accesible db for everyone
        - Will have to change util.py to connect to new db
    2. check the ouput for application
    3. Also we need to train more languages.
    4. Add more text files

2. KWIC
    1. we should highlight the selected word in each sentence 
    2. Check the length of words on each side of selected word
    3. sentence by sentence


3. CLUSTERING
    1. We should adjust our cluster algorithms
    2. Apply various algorithms to our cluster_model.py.
    3. Cluster after user search word
        - For example, if we select the word excellent, then find a sentence such as: He was an excellent journalist and a very fine man, after the cluster, we expect to get the sentence like he is a very good man.
    5. Also need to set a default k value...
        - Elbow Method 
        - will try to determine default k based on length of characters in selected 
    6. Evaluate quality of cluster
Other Changes for Clustering:
1. review codes we have pushed to the base github repo @all
2. with models we had train more languages, train_model. py to database, cluster_model. py to get word2vec model(it doesn't need to store database so everyone can do it)@all
3. test every py module and welcome to commit bugs we everyone find @all
4. with logging module add logs before and after important events @all

# Customer Requirements:
1. Show the keyword highlighted in the output.
2. Show all the keywords output in the middle of the page.
3. Changing the cluster method to show the precise keyword output.

