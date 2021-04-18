from typing import Any
from collections import defaultdict
import json

from src.train.result_model import TResult
from src.train.store import StoreData
from src.util import language_dict, language_list, db_config, cluster_model_file
from src.service import AppService
from flask import Flask, render_template, request, redirect, url_for, flash


app = Flask(__name__)

# TODO: need to change with the selection different language
appService = AppService()


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
        if not appService.udt_pre_model:
            appService.config_udpipe(language_name)
        appService.find_service(language_name, sel_word)
    return render_template('result.html', input_data={"language_name": language_name,
                                                      "sel_word": sel_word,
                                                      "sel_result": appService.sel_result})


@app.route('/find2', methods=['POST'])
def find2():
    language_name, sel_word = None, None
    if request.method == 'POST':
        language_name = request.form['sellanguage']
        sel_word = request.form['selword']
        if not appService.udt_pre_model:
            appService.config_udpipe(language_name)
        appService.find_service(language_name, sel_word)
    return render_template('result.html', input_data={"language_name": language_name,
                                                      "sel_word": sel_word,
                                                      "sel_result": appService.sel_result})


@app.route('/cluster', methods=['POST'])
def cluster():
    """
    this method is mainly to solve the cluster question

    After getting form data, begining cluster
    finally return cluster example sentences
    :return:cluster.html
    """
    if request.method == 'POST':
        language_name = request.form['languageName']
        cluster_number = request.form['clusterNumber']
        sel_tag = request.form['tagInput1']
        cluster_input_sentence = appService.pos_dict[sel_tag]
        if not appService.udt_pre_model:
            appService.config_udpipe(language_name)
        cluser_model_file = cluster_model_file[language_name]
        cluster_result = appService.cluster_sentences(language_name, cluser_model_file, cluster_input_sentence, cluster_number)
        return render_template('cluster.html', cluster_number=cluster_number, cluster_result=cluster_result)


if __name__ == '__main__':
    app.run(port=3000, debug=True)
