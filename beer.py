import pysolr


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

    def update_solr(self):
        solr = pysolr.Solr('http://solr.csse.rose-hulman.edu:8983/solr/beerbase/', timeout=5)
        results = solr.search(q='beer_id:' + self.id, fq=[], rows=1)
        if len(results.docs) == 1:
            print('Already inserted previously.')
            return False
        solr.add([self])
        results = solr.search(q='beer_id:' + self.id, fq=[], rows=1)
        if len(results.docs) == 1:
            print('Inserted correctly.')
            return True
        print('Query after insertion failed.')
        return False
