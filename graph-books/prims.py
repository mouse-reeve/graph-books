''' apply prims algorithm to the weighted books graph '''
import logging

from graph_service import GraphService
graph = GraphService()

def prims():
    ''' Prim's algorithm (more or less) '''
    # initialize the book nodes with the necessary fields
    q = 'MATCH (n:book) SET n.weight = 0, n.available = True, ' \
        'n.mstNodeId = ""'
    graph.query(q)

    # start with the True Confessions of Charlotte Doyle
    logging.debug('Setting weight on first node')
    q = 'MATCH (n:book) WHERE n.isbn = "9780380714759" ' \
        'SET n.weight = 1'
    graph.query(q)

    while True:
        # Find the weightiest available node
        q = 'MATCH (n:book) WHERE n.weight > 0 AND n.available ' \
            'RETURN n ORDER BY n.weight DESC limit 1'
        nodes = graph.query(q)

        # algorithm is complete when there are no available nodes
        if not len(nodes):
            break

        node = nodes[0][0]

        # find the highest weighed node already in the mst graph
        connector_node = None
        weight = 0
        q = 'MATCH (n:book) - [r] - (b:book) ' \
            'WHERE id(n) = %d AND NOT b.available RETURN b ' \
            'ORDER BY r.weight DESC limit 1' % (node._id)
        connectors = graph.query(q)

        # this is the first node in the graph. if not, trouble
        if len(connectors) and len(connectors[0]):
            q = 'MATCH n - [r] - b ' \
                'WHERE id(n) = %d AND id(b) = %d ' \
                'RETURN r.weight' % (node._id, connectors[0][0]._id)
            weight = graph.query(q)[0][0]

            # get the equivalent node from the MST graph
            q = 'MATCH n WHERE id(n) = %d RETURN n' % \
                connectors[0][0].properties['mstNodeId']
            nodes = graph.query(q)
            connector_node = nodes[0][0]

        # these two nodes will reference each other
        q = 'MATCH n WHERE id(n) = %d SET n.available=False' % node._id
        graph.query(q)

        mst_node = graph.add_node('mstBook', {
            'title': node.properties['title'],
            'isbn': node.properties['isbn'],
            'weight': weight
        })
        q = 'MATCH n WHERE id(n) = %d SET n.mstNodeId = %d' % (node._id, mst_node._id)
        graph.query(q)

        if connector_node:
            graph.relate_nodes(connector_node._id, mst_node._id, 'Knows')

        # re-weight all the nodes
        q = 'MATCH n - [r] - b ' \
            'WHERE id(n) = %d AND r.weight > b.weight ' \
            'SET b.weight = r.weight' % node._id
        graph.query(q)

if __name__ == '__main__':
    prims()
