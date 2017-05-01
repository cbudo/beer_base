from flask import Flask, render_template, jsonify, request
import pysolr
import re
from config import cassandra_cluster
from cassandra.cluster import Cluster

app = Flask(__name__)
cluster = Cluster(cassandra_cluster)
session = cluster.connect('brewbase')


@app.route("/")
def index():
    return render_template("landing_body.html")
	
@app.route("/beer/<int:beer_id>")
def beer(beer_id):
	rows = session.execute('SELECT * FROM beer WHERE beer_id = {} LIMIT 1'.format(beer_id))
	beer_info = rows[0]
	return render_template("beer.html", beer = beer_info)

@app.route("/brewery/<int:brewery_id>")
def brewery(brewery_id):
	rows = session.execute('SELECT * FROM brewery WHERE brewery_id = {} LIMIT 1'.format(brewery_id))
	brewery_info = rows[0]
	return render_template("brewery.html", brewery = brewery_info)

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
