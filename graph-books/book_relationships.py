''' create a graph solely containing books with weighted relationships '''
import logging

from graph_service import GraphService
graph = GraphService()


def create_book_graph():
    ''' give more value to certain connections '''

    logging.debug('weight nodes')
    # weight for now is 1 for everything
    q = 'MATCH n SET n.weight = 1'
    graph.query(q)

    logging.debug('building relationships')
    # create relationships
    q = 'MATCH (n1:book) -- r -- (n2:book) ' \
        'WHERE NOT "book" IN LABELS(r) ' \
        'WITH n1, n2, COLLECT(r) AS rels, SUM(r.weight) AS w ' \
        'CREATE (n1) - [:Knows {weight: w}] -> (n2)'
    graph.query(q)
    # TODO: this is creating duplicate relationships, and adding a
    # conditional to only pick nodes with no relationship isn't working

if __name__ == '__main__':
    create_book_graph()
