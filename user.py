from py2neo import Graph, Node, NodeSelector

g = Graph('http://neo4j.csse.rose-hulman.edu:7474/db/data', user='neo4j', password='TrottaSucks')
selector = NodeSelector(g)


class User:
    def __init__(self, username, name=None):
        self.username = username
        self.name = name

    def submit2neo4j(self):
        tx = g.begin()
        valid = g.run('MATCH (b:User { username: \'%s\'}) return b' % self.username)
        for v in valid:
            if v[0]['username'] == self.username:
                print('User with this username already exists')
                return True

        a = Node("User", username=self.username, name=self.name)
        tx.create(a)
        tx.commit()

        insertedCorrectly = g.run('MATCH (b:User { username: \'%s\'}) return b' % self.username)
        for v in insertedCorrectly:
            if v[0]['username'] == self.username:
                return True
            else:
                return False

    def deleteFromneo4j(self):
        g.run('MATCH (b:User { username: \'%s\' }) detach delete b' % self.username)
        successful = g.run('MATCH (b:User { username: \'%s\'}) return b' % self.username)
        for v in successful:
            if v[0]['username'] == self.username:
                print('Not deleted successfully')
                return False
            else:
                return True


if __name__ == '__main__':
    user = User('test_username', 'test name')
    print user.submit2neo4j()
    user.deleteFromneo4j()
