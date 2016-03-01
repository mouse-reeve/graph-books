''' builds a graph from merged books input json '''

import json
import logging
import sys
import urllib2

from graph_service import GraphService
graph = GraphService()


def add_books(json_file_url):
    ''' enter all books and related data '''
    response = urllib2.urlopen(json_file_url)
    data = json.loads(response.read())

    for item in data:
        if 'isbn' not in item or 'title' not in item:
            logging.warn('Could not parse line, isbn or title missing: %s', item)
            continue

        book = graph.add_node('book', {
            'value': item['title'],
            'isbn': item['isbn'],
            'title': item['title']
        })

        for key, value in item.iteritems():
            if not isinstance(value, list):
                value = [value]
            if len(value) < 1:
                continue
            for field in value:
                logging.debug('Adding %s: %s', key, field)
                node = graph.find_or_add_node(key, {'value': field})
                graph.relate_nodes(book._id, node._id, 'knows')

if __name__ == '__main__':
    add_books(sys.argv[1])
