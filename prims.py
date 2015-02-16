from neo4jrestclient.client import GraphDatabase, Node


class Prims:

    ''' updates and modifies the book database '''
    def __init__(self):
        self.suppress_output = False

        self.gdb = GraphDatabase("http://localhost:7474/db/data/")

    '''
    Prim's algorithm (more or less)
    '''
    def minimum_spanning_tree(self, input_graph, output_graph):
        q = 'MATCH (n:%s) SET n.weight = 0, n.available = True, ' \
            'n.mstNodeId = ""' % input_graph
        self.gdb.query(q)

        # start with the True Confessions of Charlotte Doyle, obvi
        # TODO: make this smarter/more general
        q = 'MATCH (n:%s) WHERE n.isbn = "9780380714759" ' \
            'SET n.weight = 1' % input_graph
        self.gdb.query(q)

        while True:
            # Find the weightiest available node. just picking the first node.
            q = 'MATCH (n:%s) WHERE n.weight > 0 AND n.available ' \
                'RETURN n ORDER BY n.weight DESC limit 1' % input_graph
            nodes = self.gdb.query(q, returns=Node)

            # algorithm is complete when there are no available nodes
            if not len(nodes):
                break

            node = nodes[0][0]

            # find the highest weighed node already in the mst graph
            connector_node = None
            weight = 0
            q = 'MATCH (n:%s) - [r] - b ' \
                'WHERE id(n) = %d AND NOT b.available RETURN b ' \
                'ORDER BY r.weight DESC limit 1' % (input_graph, node.id)
            connectors = self.gdb.query(q, returns=Node)

            # this is the first node in the graph. if not, trouble
            if len(connectors) and len(connectors[0]):
                q = 'MATCH n - [r] - b ' \
                    'WHERE id(n) = %d AND id(b) = %d ' \
                    'RETURN r.weight' % (node.id, connectors[0][0].id)
                weight = self.gdb.query(q)[0][0]

                # get the equivalent node from the MST graph
                q = 'MATCH n WHERE id(n) = %d RETURN n' % \
                    connectors[0][0].properties['mstNodeId']
                nodes = self.gdb.query(q, returns=Node)
                connector_node = nodes[0][0]

                if not self.suppress_output:
                    print '%s -> %s' % (connector_node.properties['name'],
                                        node.properties['name'])

            # these two nodes will reference each other
            node.set('available', False)
            # TODO: generalize this, and other uses of particular properties
            mst_node = self.gdb.node(name=node.properties['name'],
                                     isbn=node.properties['isbn'],
                                     weight=weight)
            mst_node.labels.add(output_graph)
            node.set('mstNodeId', mst_node.id)

            if connector_node:
                connector_node.Knows(mst_node)

            # re-weight all the nodes
            q = 'MATCH n - [r] - b ' \
                'WHERE id(n) = %d AND r.weight > b.weight ' \
                'SET b.weight = r.weight' % node.id
            self.gdb.query(q)
