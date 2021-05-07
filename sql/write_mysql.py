import os
import re
from src.util import *
from cnx_mysql import *

conn
conn_cur = conn.cursor()


for lang in language_list:
    if lang in [
        'Latin'
    ]:
        file_dir = corpus_language[lang]
        path = os.getcwd()+file_dir

org_file = open(path,'r+')
org_content = org_file.read()
#org_file.close()

table_query = "INSERT INTO latin_sentences VALUES sentence (%s)"
conn_cur.execute(table_query, (org_content,))

conn.commit()
conn.close()
print(conn_cur.rowcount, "Record Inserted")
