import pysolr
from py2neo import Graph, Node, NodeSelector

g = Graph('http://neo4j.csse.rose-hulman.edu:7474/db/data', user='neo4j', password='TrottaSucks')
selector = NodeSelector(g)


class Beer:
    def __init__(self, beer_id, name=None, brewery=None, brewery_id=None, style_id=None, style=None, abv=None, ibu=None,
                 category_id=None, category=None):
        self.id = beer_id
        self.name = name
        self.brewery = brewery
        self.brewery_id = brewery_id
        # Optional For Steve
        self.style_id = style_id
        # Not Optional For Steve (unless really difficult for you)
        self.style = style
        self.abv = abv
        self.ibu = ibu
        # Optional For Steve
        self.category_id = category_id
        # You get it...
        self.category = category

    def submitBeer2solr(self):
        solr = pysolr.Solr('http://solr.csse.rose-hulman.edu:8983/solr/beerbase/', timeout=50)
        results = solr.search(q='beer_id:' + str(self.id), fq=[], rows=1)
        print(results.docs)
        if len(results.docs) >= 1:
            print('Already inserted previously.')
            return False
        solr.add([{
            'beer_id': self.id,
            'brew_id': self.brewery_id,
            'brewery': self.brewery.split(' '),
            'style': self.style.split(' '),
            'category': self.category.split(' '),
            'abv': self.abv,
            'ibu': self.ibu,
            'name': self.name.split(' '),
            'keywords': []
        }])
        results = solr.search(q='beer_id:' + str(self.id), fq=[], rows=1)
        if len(results.docs) >= 1:
            print('Inserted correctly.')
            return True
        print('Query after insertion failed. Beer not inserted correctly.')
        return False

    def deleteBeerFromsolr(self):
        solr = pysolr.Solr('http://solr.csse.rose-hulman.edu:8983/solr/beerbase/', timeout=50)
        results = solr.search(q='beer_id:' + str(self.id), fq=[], rows=1)
        if len(results.docs) == 0:
            print('Already deleted previously.')
            return False
        results = solr.delete(q="beer_id:" + str(self.id))
        if '<int name="status">0</int>' not in results:
            print('Delete failed.')
            return False
        print('Beer deleted.')
        return True

    def submitBeer2neo4j(self):
        tx = g.begin()
        valid = g.run('MATCH (b:Beer { id: toInt(\'%s\')}) return b' % self.id)
        for v in valid:
            if v[0]['id'] == self.id:
                print('Beer with this ID already exists')
                return

        a = Node("Beer", id=self.id, brewery_id=self.brewery_id, style_id=self.style_id, abv=self.abv, ibu=self.ibu)
        tx.create(a)
        tx.commit()

        insertedCorrectly = g.run('MATCH (b:Beer { id: toInt(\'%s\')}) return b' % self.id)
        for v in insertedCorrectly:
            if v[0]['id'] == self.id:
                return True
            else:
                return False

    def deleteBeerFromneo4j(self):
        g.run('MATCH (b:Beer { id: toInt(\'%s\') }) detach delete b' % self.id)
        successful = g.run('MATCH (b:Beer { id: toInt(\'%s\')}) return b' % self.id)
        for v in successful:
            if v[0]['id'] == self.id:
                print('Not deleted successfully')
                return False
            else:
                return True
