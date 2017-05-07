from server import app
from py2neo import Graph
import pysolr
import schedule
import time
import config
import threading


class Updatr:
    def __init__(self, schedule_length):
        self.schedule_length = schedule_length
        self.is_running = False

    def update_databases(self):
        if self.is_running:
            return
        self.is_running = True
        if self.solr_is_up():
            self.update_solr(NotImplemented)
        if self.neo4j_is_up():
            self.update_neo4j()
        self.is_running = False

    def solr_is_up(self):
        try:
            solr = pysolr.Solr('http://solr.csse.rose-hulman.edu:8983/solr/beerbase/', timeout=5)
            solr.search(q='*:*', fq=[], rows=1)
        except pysolr.SolrError as e:
            print(e)
            return False
        return True

    def neo4j_is_up(self):
        g = Graph(config.neo4j_route, user=config.neo4j_user, password=config.neo4j_password)
        selector = g.run('MATCH (n:Beer) WHERE n.id = -1 RETURN n')
        try:
            return selector.id is not None
        except:
            return False

    def update_solr(self, item_to_insert):
        solr = pysolr.Solr('http://solr.csse.rose-hulman.edu:8983/solr/beerbase/', timeout=5)
        if item_to_insert.beerid is None:
            results = solr.search(q='beer_id:' + item_to_insert.beerid, fq=[], rows=1)
            if len(results.docs) == 1:
                print('Already inserted previously.')
                return False
            solr.add([item_to_insert])
            results = solr.search(q='beer_id:' + item_to_insert.beerid, fq=[], rows=1)
            if len(results.docs) == 1:
                print('Inserted correctly.')
                return True
            print('Query after insertion failed.')
            return False
        else:
            results = solr.search(q='brewery_id:' + item_to_insert.breweryid, fq=[], rows=1)
            if len(results.docs) == 1:
                print('Already inserted previously.')
                return False
            solr.add([item_to_insert])
            results = solr.search(q='brewery_id:' + item_to_insert.breweryid, fq=[], rows=1)
            if len(results.docs) == 1:
                print('Inserted correctly.')
                return True
            print('Query after insertion failed.')
            return False

    def update_neo4j(self):
        return NotImplemented

    def scheduler(self):
        schedule.every(self.schedule_length).seconds.do(self.update_databases())
        while True:
            schedule.run_pending()
            time.sleep(5)


if __name__ == '__main__':
    updatr = Updatr(10)
    t = threading.Thread(target=updatr.scheduler)
    t.daemon = True
    # t.start()
    app.run(host='0.0.0.0', port=5000, debug=True)  # Use this for production
    # curr_server.get_app().run()  # This is for local execution
