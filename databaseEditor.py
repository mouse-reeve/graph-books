from neo4jrestclient.client import GraphDatabase, Node
import csv
import urllib2

class DatabaseEditor:
    ''' updates and modifies the book database '''


    def __init__(self):
        githubBaseUrl = 'https://raw.githubusercontent.com/mouse-reeve'
        self.canonicalCSV = '/book-catalogue/master/canonical.csv'
        self.libraryThingCSV = '/book-catalogue/master/libraryThing.csv'

        self.gdb = GraphDatabase("http://localhost:7474/db/data/")

        # get list of graphs (each graph has a different label)
        q = 'MATCH n RETURN DISTINCT labels(n)'
        graphResponse = self.gdb.query(q)
        self.graphNames = []
        for graph in graphResponse:
            graph = graph[0][0]
            if not graph[0] or not graph[0][0]:
                print 'error parsing graph response'
                print graph
                continue
            self.graphNames.append(graph)


    def getNodeById(self, nodeId):
        q = "MATCH n WHERE id(n)=%d RETURN n" % nodeId
        nodes = self.gdb.query(q, returns=Node)
        if not nodes[0] or not nodes[0][0]:
            return False

        return nodes[0][0]


    def isValidGraphName(self, graphName):
        return graphName in self.graphNames


    def getAvailableNodes(self, graphName):
        if not self.isValidGraphName(graphName):
            print 'That\'s not a real graph. You can\'t fool me'
            return False

        q = 'MATCH (n:%s) WHERE n.weight>0' % graphName
        q += 'AND n.available RETURN n ORDER BY n.weight DESC'
        nodes = self.gdb.query(q, returns=Node)
        return nodes


    def addBooks(self, graphName):
        if not self.isValidGraphName(graphName):
            return False

        response = urllib2.urlopen(self.canonicalCSV)
        reader = csv.DictReader(response)

        for book in reversed(reader):
            print book
            # add book to graph

        # download libraryThing book csv

        # update the added books with LT data

        # build relationships for new books
        pass


    def removeField(self, graphName, fieldName, value):
        if not self.isValidGraphName(graphName):
            return False

        # Find all nodes with that field:
        q = 'MATCH (n:%s) WHERE "%s" IN n.%s RETURN n' % (graphName, value, fieldName)
        nodes = self.gdb.query(q, returns=Node)

        for node in nodes:
            node = node[0]
            # Remove field from node properties

            edges = node.relationships
            for edge in edges:
                # Reject nodes that do not contain field
                # Decrement relationship weight
                # Remove field from relationship field list
                continue


    def findByISBN(self, graphName, isbn):
        if not self.isValidGraphName(graphName):
            return False

        q = 'MATCH (n:%s) WHERE n.isbn = "%s" RETURN n' % (graphName, isbn)
        nodes = self.gdb.query(q, returns=Node)

        if len(nodes) > 0 and len(nodes[0]) > 0:
            return nodes[0][0]
        else:
            # checks for alternate ISBN format used by LibraryThing
            variant = isbn[0:-1]
            q = 'MATCH (n:%s) WHERE n.isbn =~ ".*%s.*" RETURN n' % (graphName, variant)
            nodes = self.gdb.query(q, returns=Node)
            if len(nodes) > 0 and len(nodes[0]) > 0:
                return nodes[0][0]
        return False


