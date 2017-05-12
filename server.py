import re

import pysolr
from cassandra.cluster import Cluster
from flask import Flask, render_template, jsonify, request, make_response

from config import cassandra_cluster

import py2neo
from py2neo import Graph, Node, Relationship, NodeSelector

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
    return render_template("beer.html", beer=beer_info)


@app.route("/add_beer", methods=["GET", "POST"])
def add_beer():
    if request.method == "GET":
        return render_template("add_beer.html")
    beer_info = request.form
    beer_id = session.execute("SELECT next_id FROM ids where id_name = 'beer_id' LIMIT 1")[0].next_id
    result = {'applied': False}
    while not result['applied']:
        print('candidate beer_id: {}'.format(beer_id))
        cql_result = session.execute(
            "UPDATE ids SET next_id = {} WHERE id_name = 'beer_id' IF next_id = {}".format(
                beer_id + 1, beer_id))
        result['applied'] = cql_result[0].applied
        print(result['applied'])
    print(beer_id)
    try:
        brewery_id = session.execute(
            "SELECT * FROM brewery where brewery_name={} LIMIT 1 ALLOW FILTERING".format(beer_info['brewery']))[
            0].brewery_id
    except:
        brewery_id = session.execute("SELECT next_id FROM ids where id_name = 'brewery_id' LIMIT 1")[0].next_id
        result = {'applied': False}
        while not result['applied']:
            print('candidate brewery_id: {}'.format(brewery_id))
            cql_result = session.execute(
                "UPDATE ids SET next_id = {} WHERE id_name = 'brewery_id' IF next_id = {}".format(
                    brewery_id + 1, brewery_id))
            result['applied'] = cql_result[0].applied
            print(result['applied'])
        session.execute(
            "INSERT INTO brewery (brewery_id, brewery_name) VALUES ({}, '".format(brewery_id) + str(
                beer_info['brewery']) + "')")
        session.execute(
            "INSERT INTO brewery_update (id, name, city, state, country, in_neo4j, in_solr) VALUES({},\'{}\','null','null','null', FALSE, FALSE)".format(
                brewery_id, beer_info['brewery']))
    style_id = -1
    category_id = -1
    if not beer_info['srm']:
        srm = -1
    else:
        srm = beer_info['srm']
    session.execute(
        "INSERT INTO beer_update(id, abv, brewery, brewery_id, category, category_id, ibu, in_neo4j, in_solr, name, style, style_id) VALUES({},{},\'{}\',{}, \'{}\', {},{},{},{},\'{}\',\'{}\',{})".format(
            beer_id, beer_info['abv'], beer_info['brewery'], brewery_id, beer_info['category'], category_id,
            beer_info['ibu'], False, False,
            beer_info['name'], beer_info['style'], style_id))
    session.execute(
        "INSERT INTO beer (beer_id, abv, beer_name, brewery_id, category_id, description, ibu, srm, style_id) VALUES ({}, {}, \'{}\', {}, {}, \'{}\', {}, {}, {})".format(
            beer_id, beer_info['abv'], beer_info['name'], brewery_id, category_id, beer_info['description'],
            beer_info['ibu'], srm, style_id))
    rows = session.execute('SELECT * FROM beer WHERE beer_id = {} LIMIT 1'.format(beer_id))
    beer_info = rows[0]
    return render_template("beer.html", beer=beer_info)


@app.route("/brewery/<int:brewery_id>")
def brewery(brewery_id):
    rows = session.execute('SELECT * FROM brewery WHERE brewery_id = {} LIMIT 1'.format(brewery_id))
    brewery_info = rows[0]
    return render_template("brewery.html", brewery=brewery_info)


@app.route("/add_brewery", methods=["GET", "POST"])
def add_brewery():
    if request.method == "GET":
        return render_template("add_brewery.html")
    brewery_info = request.form
    try:
        brewery_id = session.execute(
            "SELECT * FROM brewery where brewery_name={} LIMIT 1 ALLOW FILTERING".format(brewery_info['name']))[
            0].brewery_id
    except:
        brewery_id = session.execute("SELECT next_id FROM ids where id_name = 'brewery_id' LIMIT 1")[0].next_id
        result = {'applied': False}
        while not result['applied']:
            print('candidate brewery_id: {}'.format(brewery_id))
            cql_result = session.execute(
                "UPDATE ids SET next_id = {} WHERE id_name = 'brewery_id' IF next_id = {}".format(
                    brewery_id + 1, brewery_id))
            result['applied'] = cql_result[0].applied
            print(result['applied'])
    session.execute(
        "INSERT INTO brewery (brewery_id, brewery_name, address1, address2, city, state, country, code, phone, website, description) VALUES ({}, '{}','{}','{}','{}','{}','{}','{}','{}','{}','{}')".format(
            brewery_id, brewery_info['name'], brewery_info['address1'], brewery_info['address2'], brewery_info['city'],
            brewery_info['state'],
            brewery_info['country'], brewery_info['code'], brewery_info['phone'], brewery_info['website'],
            brewery_info['description']))
    session.execute(
        "INSERT INTO brewery_update (id, name, city, state, zip, country, in_neo4j, in_solr) VALUES({},\'{}\','{}','{}','{}','{}',{},{})".format(
            brewery_id, brewery_info['name'], brewery_info['city'], brewery_info['state'], brewery_info['code'],
            brewery_info['country'], False,
            False))
    rows = session.execute('SELECT * FROM brewery WHERE brewery_id = {} LIMIT 1'.format(brewery_id))
    brewery_info = rows[0]
    return render_template("brewery.html", brewery=brewery_info)


@app.route("/search")
def search():
    return render_template("search_body.html")


@app.route("/perform_search", methods=['POST'])
def perform_search():
    solr = pysolr.Solr('http://solr.csse.rose-hulman.edu:8983/solr/beerbase/', timeout=50)

    query = request.form['query'] #Change to request.form['username'] for the new search by user function
    if query is None or query == '':
        return jsonify(results=[], status_code=200)
    word_list = query.split(' ')

    filter_string = request.form['filter']
    in_filters = []
    if filter_string is not None and filter_string != '':
        in_filters = filter_string.split(' ')

    entity = 'beer'
    if request.form['entity'] is not None and request.form['entity'] != '':
        entity = request.form['entity']

    if len(word_list) == 0:
        return jsonify(results=[], status_code=200)

    op = 'OR'

    cleaned_query, cleaned_words = clean_words(word_list)

    temp_query = get_filter_query(cleaned_words, in_filters)

    if temp_query != '':
        cleaned_query = temp_query

    if entity == 'beer':
        filter_queries = ['abv:*']
    else:
        filter_queries = ['country:*']

    results = solr.search(q=cleaned_query, fq=filter_queries, rows=100, op=op)

    return jsonify(results=results.docs, status_code=200)


@app.route("/perform_user_rec", methods=['POST'])
def perform_user_rec():
    g = Graph('http://neo4j.csse.rose-hulman.edu:7474/db/data', user='neo4j', password='TrottaSucks')
    selector = NodeSelector(g)
    user = request.form['username']

    if user is None or user == '':
        return jsonify(results=[], status_code=200)

    user = g.run('MATCH (u:User { username: \'%s\' }) return u.username' % username)
    validCheck = ''
    for u in user:
        validCheck = 'checked'
    if validCheck == '':
        print("No users with that name in the database")
        return

    suggestedBeers = g.run('MATCH (:User {username:\'%s\'})-[:LIKES*3]-(b:Beer) with DISTINCT b ORDER BY b.id LIMIT 30 RETURN b' % username)
    removeLiked = g.run('MATCH (:User {username:\'%s\'})-[:LIKES]-(b:Beer) return b' % user)

    allBeersSuggested = []
    for beer in suggestedBeers:
        allBeersSuggested.append(beer[0])

    beersToRemove = []
    for like in removeLiked:
        beersToRemove.append(like[0])

    toBeSuggested =list(set(allBeersSuggested)^set(beersToRemove))

    print(toBeSuggested)

    return toBeSuggested


def clean_words(word_list):
    cleaned_query = ''
    cleaned_words = []
    for word in word_list:
        if re.match(r"^[a-zA-Z0-9_]*$", word) is None:
            continue
        elif cleaned_query == '':
            cleaned_query = word
        else:
            cleaned_query += ' ' + word
        cleaned_words.append(word)
    return cleaned_query, cleaned_words


def get_filter_query(cleaned_words, in_filters):
    temp_query = ''
    for x in range(0, len(in_filters)):
        if re.match(r"^[a-zA-Z0-9_]*$", in_filters[x]) is None:
            continue
        to_add = ''
        for cleaned_word in cleaned_words:
            if to_add == '':
                to_add = in_filters[x] + ':' + '(' + cleaned_word
            else:
                to_add += ' AND ' + cleaned_word
        to_add += ') '
        temp_query += to_add
    return temp_query


@app.route("/create_user", methods=["GET", "POST"])
def create_user():
    if request.method == 'GET':
        return render_template('create_user.html')
    user = request.form
    try:
        session.execute("INSERT INTO user (username, name) VALUES ('{}','{}')".format(user['username'], None))
        session.execute("INSERT INTO user_update (username, name, in_neo4j VALUES ('{}', '{}', FALSE )".format(user['username'], None))
        username = session.execute("SELECT * FROM user WHERE username = '{}'".format(user['username']))[0].username
        return make_response(jsonify(result=username), 200)
    except:
        return make_response(jsonify(result=None), 404)


@app.route("/login", methods=["GET", "POST"])
def login_user():
    if request.method == 'GET':
        return render_template('login.html')
    user = request.form
    try:
        return make_response(jsonify(result=session.execute("SELECT * FROM user WHERE username = '{}'".format(user['username']))[0].username), 200)
    except:
        return make_response(jsonify(result=None), 404)
