import neo4jrestclient.client as client
from neo4jrestclient.client import GraphDatabase

class GraphController:
    def __init__(self):
        print 'initialize'
        self.db = GraphDatabase("http://localhost:7474/db/data/")

    def getNodeById(self, nodeId):
        try:
            nodeId = int(nodeId)
        except:
            return False

        q = 'MATCH (node) WHERE id(node) = %d return node' % nodeId
        node = self.db.query(q, returns=(client.Node))
        if len(node) != 1 or len(node[0]) < 1:
            return False

        node = node[0][0]
        return self.buildNodeJson(node)

    def buildNodeJson(self, node):
        data = {
            'properties': node.properties,
            'labels': [],
            'relationships': []
        }

        for label in node.labels:
            data['labels'].append(label._label)

        for relationship in node.relationships:
            data['relationships'].append({
                'properties': relationship.properties,
                'type': relationship.type,
                'end': relationship.end.properties
                })
        return data


