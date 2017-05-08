class Brewery:
    def __init__(self, brewery_id, name, zip_code, city, state, country):
        self.id = brewery_id
        self.name = name
        self.zip = zip_code
        self.city = city
        self.state = state
        self.country = country

    def update_solr(self):
        results = solr.search(q='brewery_id:' + self.id, fq=[], rows=1)
        if len(results.docs) == 1:
            print('Already inserted previously.')
            return False
        solr.add([self])
        results = solr.search(q='brewery_id:' + self.id, fq=[], rows=1)
        if len(results.docs) == 1:
            print('Inserted correctly.')
            return True
        print('Query after insertion failed.')
        return False
