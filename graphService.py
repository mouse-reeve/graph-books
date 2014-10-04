import neo4jrestclient.client as client
from neo4jrestclient.client import GraphDatabase

class GraphService:
    def __init__(self):
        print 'initialize'
        self.db = GraphDatabase("http://localhost:7474/db/data/")

    def getNodeById(self, nodeId):
        try:
            nodeId = int(nodeId)
        except:
            return False

        q = 'MATCH (node) WHERE id(node) = %d RETURN node' % nodeId
        node = self.db.query(q, returns=(client.Node))
        if len(node) != 1 or len(node[0]) < 1:
            return False

        return node[0][0]

    def getNodesByName(self, name):
        q = 'MATCH (node) WHERE node.name =~ "(?i).*%s.*" RETURN node' % name
        nodes = self.db.query(q, returns=(client.Node))
        if len(nodes) < 1 or len(nodes[0]) < 1:
            return False

        return nodes

    def createRelationship(self, startId, relationship, endId):
        start = self.getNodeById(startId)
        end = self.getNodeById(endId)

        start.relationships.create(relationship, end)
        return True

