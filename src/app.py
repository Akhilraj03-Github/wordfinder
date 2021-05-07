import os
import sys
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)

from typing import Any
from collections import defaultdict
import json

from src.train.result_model import TResult
from src.train.store import StoreData
from src.util import language_dict, language_list, db_config, word2vec_language
from src.service import AppService, AppContext
from flask import Flask, render_template, request, redirect, url_for, flash


app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# TODO: need to change with the selection different language
app_service = AppService()
app_context = AppContext


@app.route('/')
def index():
    """
    This is the index web page
    :return:index.html
    """
    return render_template('index.html')


@app.route('/find', methods=['POST'])
def find():
    """
    this method mainly solve /find request
    first, according to form data, select by database to get result
    second, reorganize to certain data structures
    finally, render to result.html
    :return: result.html
    """
    language_name, sel_word = None, None
    if request.method == 'POST':
        language_id = request.form['sellanguage']
        sel_word = request.form['selword']
        language_name = language_dict[language_id]
        app_context.sel_word = sel_word
        app_context.sel_language = language_name
        if not app_service.udt_pre_model:
            app_service.config_udpipe(language_name)
        app_service.find_service(language_name, sel_word)
        sel_result_kwic = app_service.kwic(sel_word, app_service.sel_result)
        app_context.sel_result_kwic = sel_result_kwic
    return render_template('result.html', input_data={"language_name": language_name,
                                                      "sel_word": sel_word,
                                                      "sel_result": sel_result_kwic})


@app.route('/find2', methods=['POST'])
def find2():
    language_name, sel_word = None, None
    if request.method == 'POST':
        language_name = request.form['sellanguage']
        sel_word = request.form['selword']
        app_context.sel_word = sel_word
        app_context.sel_language = language_name
        if not app_service.udt_pre_model:
            app_service.config_udpipe(language_name)
        app_service.find_service(language_name, sel_word)
        sel_result_kwic = app_service.kwic(sel_word, app_service.sel_result)
        app_context.sel_result_kwic = sel_result_kwic
    return render_template('result.html', input_data={"language_name": language_name,
                                                      "sel_word": sel_word,
                                                      "sel_result": sel_result_kwic})


@app.route('/cluster', methods=['POST'])
def cluster():
    """
    this method is mainly to solve the cluster question
    After getting form data, beginning cluster
    finally return cluster example sentences
    :return:cluster.html
    """
    if request.method == 'POST':
        language_name = request.form['languageName']
        cluster_number = request.form['clusterNumber']
        sel_tag = request.form['tagInput1']
        # TODO: clicking the button of return previous page then clicking cluster button causes a bug
        cluster_input_sentence = app_service.pos_dict[sel_tag]
        if not app_service.udt_pre_model:
            app_service.config_udpipe(language_name)
        cluster_model_file = word2vec_language[language_name]
        cluster_result, rec_cluster_result, sentences, best_labels = app_service.cluster_sentences(
            language_name, cluster_model_file, cluster_input_sentence, cluster_number)
        if not cluster_result:
            flash("invalid input to cluster number")
            return render_template('result.html', input_data={"language_name": language_name,
                                                              "sel_word": app_context.sel_word,
                                                              "sel_result": app_context.sel_result_kwic})
        return render_template('cluster.html',
                               cluster_number=cluster_number,
                               cluster_result=cluster_result,
                               rec_cluster_result=rec_cluster_result,
                               sentences_with_labels=zip(sentences, best_labels))


if __name__ == '__main__':
    app.run(port=3000, debug=True)

