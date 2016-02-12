''' Produce a list of books from the books-only graph '''
from neo4jrestclient.client import GraphDatabase, Node

class SimpleList(object):
    ''' updates and modifies the book database '''

    def __init__(self):
        self.suppress_output = True

        self.gdb = GraphDatabase("http://localhost:7474/db/data/")

    def simple_list(self, input_graph, output_graph, output_filename=None):
        ''' run the algorithm '''
        output_file = None
        if output_filename:
            output_file = open(output_filename, 'w')

        q = 'MATCH (n:%s) SET n.weight = 0, n.available = True' % input_graph
        self.gdb.query(q)

        # find the strongest relationship
        q = 'MATCH (n:%s) - [r] - () RETURN n ' \
            'ORDER BY r.weight DESC LIMIT 1' % input_graph
        start_node = self.gdb.query(q, returns=Node)[0][0]

        previous_book = None

        while True:
            name = start_node.properties['name']
            print 'adding node %s' % name
            book = self.gdb.node(name=name,
                                 isbn=start_node.properties['isbn'])
            book.labels.add(output_graph)
            if output_file:
                output_file.write(name.encode('utf-8'))
                output_file.write('\n')

            if previous_book:
                previous_book.Knows(book)

            start_node.set('available', False)

            # reset weights
            q = 'MATCH (n:%s) SET n.weight = 0' % input_graph
            self.gdb.query(q)

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
        if output_file:
            output_file.close()
