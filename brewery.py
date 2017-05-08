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