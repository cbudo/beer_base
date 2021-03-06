import pysolr
import py2neo
from py2neo import Graph, Node, Relationship, NodeSelector

g = Graph('http://neo4j.csse.rose-hulman.edu:7474/db/data', user='neo4j', password='TrottaSucks')
selector = NodeSelector(g)

class Brewery:
    def __init__(self, brewery_id, name, zip_code, city, state, country):
        self.id = brewery_id
        self.name = name
        self.zip = zip_code
        self.city = city
        self.state = state
        self.country = country

    def submitBrewery2solr(self):
        solr = pysolr.Solr('http://solr.csse.rose-hulman.edu:8983/solr/beerbase/', timeout=5)
        results = solr.search(q='brewery_id:' + self.id, fq=[], rows=1)
        if len(results.docs) == 1:
            print('Already inserted previously.')
            return False
        if (self.name is None) or (self.city is None) or (self.state is None) or (self.country is None):
            print('Critical attributes are missing.')
            return False
        name_split = self.name.split(' ')
        city_split = self.city.split(' ')
        state_split = self.state.split(' ')
        country_split = self.country.split(' ')
        solr.add([{
            'brewery_id': self.id,
            'name': name_split,
            'city': city_split,
            'state': state_split,
            'country': country_split,
            'keywords': name_split + city_split + state_split + country_split
        }])
        results = solr.search(q='brewery_id:' + self.id, fq=[], rows=1)
        if len(results.docs) == 1:
            print('Inserted correctly.')
            return True
        print('Query after insertion failed. Brewery did not insert correctly.')
        return False

    def deleteBreweryFromsolr(self):
        solr = pysolr.Solr('http://solr.csse.rose-hulman.edu:8983/solr/beerbase/', timeout=5)
        results = solr.search(q='brewery_id:' + self.id, fq=[], rows=1)
        if len(results.docs) == 0:
            print('Already deleted previously.')
            return False
        solr.delete(brewery_id=self.id)
        results = solr.search(q='brewery_id:' + self.id, fq=[], rows=1)
        if len(results.docs) == 1:
            print('Delete failed.')
            return True
        print('Brewery deleted.')
        return False

    def submitBrewery2neo4j(self):
        tx = g.begin()
        valid = selector.select("Brewery", self.id)
        for v in valid:
            if v['id'] == self.id:
                print('Brewery with this ID already exists')
                return

        a = Node("Brewery", id=self.id, location=self.zip)
        tx.create(a)
        tx.commit()
