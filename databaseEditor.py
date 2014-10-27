from neo4jrestclient.client import GraphDatabase, Node

class DatabaseEditor:
    ''' updates and modifies the book database '''

    def __init__(self):
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
        q = 'MATCH (n:%s) WHERE n.weight>0 AND n.available RETURN n ORDER BY n.weight DESC' % graphName
        nodes = self.gdb.query(q, returns=Node)
        return nodes

    def addBooks(self, graph):
        # download canonical book csv

        # find and add new books - assumes list is ordered by date added

        # download libraryThing book csv

        # update the added books with LT data

        # build relationships for new books
        pass

    def removeField(self, fieldName, value):
        # Find all nodes with that field:

        #   Remove field from node properties

        #   Find relationships from node that include field:
        #       Decrement relationship weight
        #       Remove field from relationship field list
        pass


