from flask import Flask, render_template, jsonify, request
import pysolr
import re

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("landing_body.html")


@app.route("/search")
def search():
    return render_template("search_body.html")


@app.route("/perform_search", methods=['POST'])
def perform_search():
    solr = pysolr.Solr('http://solr.csse.rose-hulman.edu:8983/solr/beerbase/', timeout=10)
    query = request.form['query']
    if query is None or query == '':
        return jsonify([], status=200)
    cleaned_query = ''
    word_list = query.split(' ')
    if len(word_list) == 0:
        return jsonify([], status=200)
    for word in word_list:
        if re.match(r"^[a-zA-Z0-9_]*$", word) is None:
            continue
        elif cleaned_query == '':
            cleaned_query = word
        else:
            cleaned_query += ' ' + word
    filter_queries = ['abv:*']
    results = solr.search(q=cleaned_query, fq=filter_queries, rows=100, op='AND')
    return jsonify(results=results.docs, status_code=200)
