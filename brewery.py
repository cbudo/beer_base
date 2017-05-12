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
        solr = pysolr.Solr('http://solr.csse.rose-hulman.edu:8983/solr/beerbase/', timeout=50)
        results = solr.search(q='brewery_id:' + str(self.id), fq=[], rows=1)
        if len(results.docs) == 1:
            print('Already inserted previously.')
            return False
        if (self.name is None):
            print('Critical attributes are missing.')
            return False
        name_split = self.name.split(' ')
        if self.city:
            city_split = self.city.split(' ')
        else:
            city_split = []
        if self.state:
            state_split = self.state.split(' ')
        else:
            state_split = []
        if self.country:
            country_split = self.country.split(' ')
        else:
            country_split = []
        solr.add([{
            'brewery_id': self.id,
            'name': name_split,
            'city': city_split,
            'state': state_split,
            'country': country_split,
            'keywords': name_split + city_split + state_split + country_split
        }])
        results = solr.search(q='brewery_id:' + str(self.id), fq=[], rows=1)
        if len(results.docs) == 1:
            print('Inserted correctly.')
            return True
        print('Query after insertion failed. Brewery did not insert correctly.')
        return False

    def deleteBreweryFromsolr(self):
        solr = pysolr.Solr('http://solr.csse.rose-hulman.edu:8983/solr/beerbase/', timeout=50)
        results = solr.search(q='brewery_id:' + str(self.id), fq=[], rows=1)
        if len(results.docs) == 0:
            print('Already deleted previously.')
            return False
        solr.delete(q='brewery_id:' + str(self.id))
        results = solr.search(q='brewery_id:' + str(self.id), fq=[], rows=1)
        if len(results.docs) >= 1:
            print('Delete failed.')
            return False
        print('Brewery deleted.')
        return True

    def submitBrewery2neo4j(self):
        tx = g.begin()
        valid = g.run('MATCH (br:Brewery { id: toInt(\'%s\')}) return br' % self.id)
        for v in valid:
            if v[0]['id'] == self.id:
                print('Brewery with this ID already exists')
                return

        a = Node("Brewery", id=self.id, location=self.zip)
        tx.create(a)
        tx.commit()
        # insertedCorrectly = selector.select("Brewery", self.id)
        insertedCorrectly = g.run('MATCH (br:Brewery { id: toInt(\'%s\')}) return br' % self.id)
        for v in insertedCorrectly:
            if v[0]['id'] == self.id:
                return True
            else:
                return False

    def deleteBreweryFromneo4j(self):
        g.run('MATCH (br:Brewery { id: toInt(\'%s\') }) detach delete br' % self.id)
        successful = g.run('MATCH (br:Brewery { id: toInt(\'%s\')}) return br' % self.id)
        for v in successful:
            if v[0]['id'] == self.id:
                print('Not deleted successfully')
                return False
            else:
                return True
