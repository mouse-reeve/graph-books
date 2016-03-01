''' simple linear ordering '''
import logging

from graph_service import GraphService
graph = GraphService()

def simple_list():
    ''' order books based on similarity to the last few added items '''

    q = 'MATCH (n:book) SET n.weight = 0, n.available = True'
    graph.query(q)

    # find the strongest relationship
    q = 'MATCH (n:book) - [r] - (:book) RETURN n ' \
        'ORDER BY r.weight DESC LIMIT 1'
    start_node = graph.query(q)[0][0]

    previous_book = None

    while True:
        title = start_node.properties['title']
        logging.debug('adding node %s', title)
        book = graph.add_node('simpleList', {
            'title': title,
            'isbn': start_node.properties['isbn']
        })
        if previous_book:
            graph.relate_nodes(previous_book._id, book._id, 'Knows')

        q = 'MATCH n WHERE id(n) = %s SET n.available = False' % start_node._id
        graph.query(q)

        # reset weights
        q = 'MATCH (n:book) SET n.weight = 0'
        graph.query(q)

        # set the weight of connected nodes
        q = 'MATCH (b:book) - [r] - n WHERE id(b) = %d ' \
            'SET n.weight = r.weight' % (start_node._id)
        graph.query(q)

        # find the highest weighted node
        q = 'MATCH (n:book) WHERE n.available ' \
            'RETURN n ORDER BY n.weight DESC LIMIT 1'
        nodes = graph.query(q)

        if not len(nodes):
            break

        start_node = nodes[0][0]
        previous_book = book

if __name__ == '__main__':
    simple_list()
