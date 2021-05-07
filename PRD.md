## software development document


### 1 Train Corpus Acquisition
#### 1.1 wikipedia

click following link:
- https://dumps.wikimedia.org/frwiki/20210301/
- select an item with xml and bz2 format, such as 
 frwiki-20210301-pages-articles-multistream3.xml-p2550823p2977214.bz2 138.8 MB
 
 following is mirror link and faster to download:
 https://ftp.acc.umu.se/mirror/wikimedia.org/dumps/frwiki/20210320/
- replace fr of link the above with another name of languages.

#### 1.2 how to extract corpus

- first download source code of wikiextractor
- cd to wikiextractor
- execute this commond:
  python -m wikiextractor.WikiExtractor -o . --process 2 -b 512K --json 
  /home/zglg/SLU/psd/corpus/english/enwiki-20210301-pages-articles-multistream11.xml-p6899367p7054859.bz2
  
- get json files.
- execute codes following: 
  wordfinder/src/corpusget/extractwiki.py
  
### 2 Train Corpus

