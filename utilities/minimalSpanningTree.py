import neo4jrestclient.client as client
from neo4jrestclient.client import GraphDatabase

gdb = GraphDatabase("http://localhost:7474/db/data/")
graphname = 'mstBooks'

# TODO: find a non-crappy way to set a start node
startId = 94

# Setup the original book nodes
q = 'MATCH n RETURN n'
books = gdb.query(q, returns=(client.Node))
nodeTotal = len(books)
print nodeTotal

for node in books:
    node = node[0]
    node.set('weight', 0)
    node.set('available', True)
    node.set('mstNodeId', None)
    if node.id == startId:
        node.set('weight', 1)

thereAreStillNodesOutThere = True

while nodesAdded < nodeTotal:
    print '--------------------------------   Finding available, weighted nodes'
    q = 'MATCH n WHERE n.weight>0 AND n.available RETURN n ORDER BY n.weight DESC'
    nodes = gdb.query(q, returns=(client.Node))
    print len(nodes)
    if not len(nodes):
        thereAreStillNodesOutThere = False
        break

    # TODO: assess whether picking up off the top is ideal/acceptable
    node = nodes[0][0]

    print '----------------------------------------  Finding place for new node'
    bestEdge = None
    print 'getting relationships'
    edges = node.relationships

    print 'assessing edges for place to connect to MST'
    for edge in edges:
        edgeNode = edge.start if edge.start.id != node.id else edge.end
        if edgeNode.properties['available']:
            continue

        if not bestEdge or bestEdge.properties['weight'] < edge.properties['weight']:
            print 'possible edge with weight %d found' % edge.properties['weight']
            bestEdge = edge

    if bestEdge:
        print 'picked edge with weight %d' % bestEdge.properties['weight']

    if bestEdge:
        originalConnectorNode = bestEdge.start if bestEdge.end.id == node.id else bestEdge.end

        q = 'MATCH (node) WHERE id(node) = %d RETURN node' % nodeId
        connectorNode = gdb.query(q, returns=(client.Node))[0][0]
    else:
        connectorNode = None
        print 'IS THIS NODE 1 OR WHAT???'

    print '-------------------------------------------------  Creating new node'
    node.set('available', False)
    newNode = gdb.node(source=node.id)
    newNode.labels.add(graphName)
    newNode.properties = node.properties

    node.set('mstNodeId', newNode.id)
    print 'created node with id %d' % newNode.id

    if connectorNode:
        newNode.Know(connectorNode)


    print 're-weighting available nodes that touch this one'
    for edge in edges:
        edgeNode = edge.start if edge.start.id != node.id else edge.end
        if not edgeNode.properties['available']:
            continue
        if edgeNode.properties['weight'] < edge.properties['weight']:
            edgeNode.set('weight', edge.properties['weight'])

    print 'WHEW!!\n\n\n'


