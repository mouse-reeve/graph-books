from neo4jrestclient.client import GraphDatabase, Node


class SimpleList:

    ''' updates and modifies the book database '''
    def __init__(self):
        self.suppress_output = False

        self.gdb = GraphDatabase("http://localhost:7474/db/data/")

    def simple_list(self, input_graph, output_graph):
        q = 'MATCH (n:%s) SET n.weight = 0, n.available = True' % input_graph
        self.gdb.query(q)

        # find the strongest relationship
        q = 'MATCH (n:%s) - [r] - () RETURN n ' \
            'ORDER BY r.weight DESC LIMIT 1' % input_graph
        start_node = self.gdb.query(q, returns=Node)[0][0]

        previous_book = None

        while True:
            print 'adding node %s' % start_node.properties['name']
            book = self.gdb.node(name=start_node.properties['name'],
                                 isbn=start_node.properties['isbn'])
            book.labels.add(output_graph)

            if previous_book:
                previous_book.Knows(book)

            start_node.set('available', False)

            # set the weight of connected nodes
            q = 'MATCH (b:%s) - [r] - n WHERE id(b) = %d ' \
                'SET n.weight = r.weight' % (input_graph, start_node.id)
            self.gdb.query(q)

            # find the highest weighted node
            q = 'MATCH (n:%s) WHERE n.available ' \
                'RETURN n ORDER BY n.weight DESC LIMIT 1' % input_graph
            nodes = self.gdb.query(q, returns=Node)

            if not len(nodes):
                break

            start_node = nodes[0][0]
            previous_book = book
