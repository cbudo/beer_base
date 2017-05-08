import py2neo
from py2neo import Graph, Node, Relationship, NodeSelector

g = Graph('http://neo4j.csse.rose-hulman.edu:7474/db/data', user='neo4j', password='TrottaSucks')
selector = NodeSelector(g)

class Beer:
    def __init__(self, beer_id, name, brewery, brewery_id, style_id, abv, ibu, category, ):
        self.id = beer_id
        self.name = name
        self.brewery = brewery
        self.brewery_id = brewery_id
        self.style_id = style_id
        self.abv = abv
        self.ibu = ibu
        self.category = category

    def submitBeer2neo4j(self):
        tx = g.begin()
        valid = selector.select("Beer", self.id)
        for v in valid:
            if v['id'] == self.id:
                print('Beer with this ID already exists')
                return

        a = Node("Beer", id=self.id, brewery_id=self.brewery_id, style_id=self.style_id, abv=self.abv, ibu=self.ibu)
        tx.create(a)
        tx.commit()
