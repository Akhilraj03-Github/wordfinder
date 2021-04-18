# This module is mainly used to store our train result to database
# at present this module supports storing for multiple languages.
# use and refer interfaces between mysql and python by
# https://dev.mysql.com/doc/connector-python/en/connector-python-example-connecting.html
# pymysql is the library for us to use between python and mysql

from __future__ import print_function

import pymysql
from typing import List

from src.train.result_model import TResult
from src.util import db_config,language_dict


class StoreData(object):
    def __init__(self,db_user,db_pwd,db_host,db_name):
        """
        construct databse configurations of mysql
        :param db_user:
        :param db_pwd:
        :param db_host:
        :param db_name:
        """
        self.DB_USER = db_user
        self.DB_PWD = db_pwd
        self.DB_HOST = db_host
        self.DB_NAME = db_name
        self.cnx = None

    def db_connect(self):
        """
        connect mysql and return connection object

        remember: should create connection as few as possible
        :return: connection to database object
        """
        try:
            if self.DB_NAME:
                self.cnx = pymysql.connect(user=self.DB_USER,
                                           password=self.DB_PWD,
                                           host=self.DB_HOST,
                                           database=self.DB_NAME,)
            else:
                self.cnx = pymysql.connect(user=self.DB_USER,
                                           password=self.DB_PWD,
                                           host=self.DB_HOST)
        except pymysql.connect.Error as err:
            print(err)
        print('connection succeed!')
        return self.cnx

    def create_database(self,cursor):
        """
        This method is mainly used to create mysql database
        :param cursor: cnx.cursor()
        :return:
        """
        try:
            if not self.DB_NAME:
                self.DB_NAME = db_config['db_name']
            cursor.execute(
                "CREATE DATABASE IF NOT EXISTS {} DEFAULT CHARACTER SET 'utf8'".format(self.DB_NAME))
            print('database %s creation succeed' % self.DB_NAME)
        except pymysql.connect.Error as err:
            print("Failed creating database: {}".format(err))
            exit(1)

    def create_tables(self, cursor, tables: dict, tables_sentences: dict):

        try:
            cursor.execute("USE {}".format(self.DB_NAME))
        except pymysql.connect.Error as err:
            print(err)

        for table_name in tables:
            table_description = tables[table_name]
            try:
                print("Creating table {}: \n".format(table_name),end='')
                cursor.execute(table_description)
                print('table %s creation succeed\n' % table_name)
            except pymysql.connect.Error as err:
                print("Error occured creating tables coz of {}".format(err))

        for table_name in tables_sentences:
            table_description = tables_sentences[table_name]
            try:
                print("Creating table {}: \n".format(table_name),end='')
                cursor.execute(table_description)
                print('table %s creation succeed\n' % table_name)
            except pymysql.connect.Error as err:
                print("Error occured creating tables coz of {}".format(err))

        cursor.close()

    def insert_data(self,cursor,rows: List[TResult],language_name):
        """
        insert rows to table
        :param cursor
        :param rows: results
        :param language_name
        :return: List[TResult]
        """
        add_sentence = ("INSERT INTO " + language_name + "_sentences "
                                                         "(sentence) "
                                                         "VALUES (%s)")
        add_words = ("INSERT INTO  " + language_name + "_wordpos "
                                                       "(word, pos_tag, sentence) "
                                                       "VALUES (%s, %s, %s)")
        try:
            # First insert sentence table for a specific language
            cursor.execute(add_sentence,rows[0].sentence)
            insert_sentence_id = cursor.lastrowid
            # Insert TResults batchly
            data = [(row.word,row.pos_tag,insert_sentence_id) for row in rows]
            cursor.executemany(add_words,data)
            self.cnx.commit()
            print('insert data succeed')
        except pymysql.connect.error as e:
            self.cnx.rollback()
            # TODO: add log
            print('insert error',e, rows)

    def select_data(self,cursor,word,language):
        """
        This method is mainly used to select data from database
        by input word from web interface

        The returning result can be mapped to TResult
        :param cursor:
        :param word: word wanted to find
        :param language: word subjected to which language
        :return:
        """
        # "select * from Chinese_wordpos as w left join Chinese_sentences as s on w.sentence=s.id limit 1000;"
        try:
            query = ("SELECT word, pos_tag, sentence FROM %s_wordpos "
                     "WHERE  word = %s") % (language,word)
            cursor.execute(query)
            rows = cursor.fetchall()
            return rows
        except pymysql.connect.error as err:
            print("Query error due to {}".format(err))


if __name__ == '__main__':
    """The ddl srcipt should be executed only once a time """
    TABLES = {}
    for language in language_dict.values():
        TABLES[language + '_wordpos'] = (
                                            "CREATE TABLE IF NOT EXISTS  `%s_wordpos` ("
                                            "  `id` int(11) NOT NULL AUTO_INCREMENT,"
                                            "  `word` varchar(256) NOT NULL,"
                                            "  `pos_tag` varchar(64) NOT NULL,"
                                            "  `sentence` TEXT NOT NULL,"
                                            "  `create_time` timestamp NULL default CURRENT_TIMESTAMP,"
                                            "  PRIMARY KEY (`id`)"
                                            ") ENGINE=InnoDB") % (language,)

    TABLES_SENTENCES = {}
    for language in language_dict.values():

        TABLES_SENTENCES[language + '_sentences'] = (
                                                        "CREATE TABLE IF NOT EXISTS  `%s_sentences` ("
                                                        "  `id` int(11) NOT NULL AUTO_INCREMENT,"
                                                        "  `sentence` TEXT NOT NULL,"
                                                        "  `create_time` timestamp NULL default CURRENT_TIMESTAMP,"
                                                        "  PRIMARY KEY (`id`)"
                                                        ") ENGINE=InnoDB") % (language,)

    # so in alpha version we should install mysql in local
    # put config info of database to db_config variable
    store_data = StoreData(db_config['user'],
                           db_config['password'],
                           db_host=db_config['db_host'],
                           db_name=None)
    conn = store_data.db_connect()
    store_data.create_database(conn.cursor())
    store_data.create_tables(conn.cursor(), TABLES, TABLES_SENTENCES)
    print('Done succeed~')
