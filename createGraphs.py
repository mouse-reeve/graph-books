from neo4jrestclient.client import GraphDatabase
import csv
import json
import urllib2
import math

import utilities


class CreateGraphs:

    ''' Create the Databases '''
    def __init__(self):
        github_url = 'https://raw.githubusercontent.com/mouse-reeve'
        self.merged_book_data = github_url + '/book-catalogue/master/merged-data.json'

        self.suppress_output = True

        self.utils = utilities.Utilities()

        self.gdb = GraphDatabase("http://localhost:7474/db/data/")

    def add_books(self):
        graph_name = 'bookData'

        # download libraryThing json export
        response = urllib2.urlopen(self.merged_book_data)
        data = json.load(response)

        for datum in data:
            row = datum
            if 'isbn' not in row or 'title' not in row:
                continue

            name = row['title']
            book = self.utils.create_node(name, 'book', graph_name)
            for key, value in row.iteritems():
                if len(value) > 0:
                    book.set(key, value)
                    if isinstance(value, list):
                        for item in value:
                            node = self.utils.find_or_create_node(item, key, graph_name)
                            node.Knows(book)
                    else:
                        node = self.utils.find_or_create_node(value, key, graph_name)
                        node.Knows(book)


    def create_book_graph(self):
        weights = {
            'publisher':    1,
            'purchasedAt':  2,
            'series':       3,
            'year':         3,
            'decade':       4,
            'places':       5,
            'language':     6,
            'readability':  6,
            'events':       7,
            'tags':         7,
            'type':         7,
            'recommender':  8,
            'references':   8,
            'characters':   9,
            'author':       10,
            'mood':         12
        }

        # weight all non-book nodes (currently, sets all weights to 1)
        if not self.suppress_output:
            print 'adding weights to book data graph'
        for field in weights:
            weight = weights[field]
            q = 'MATCH (n:bookData) WHERE n.contentType = "%s" ' \
                'SET n.weight = %d' % (field, weight)
            self.gdb.query(q)

        if not self.suppress_output:
            print 'creating book nodes'
        # create all book nodes
        q = 'MATCH (n:bookData) WHERE n.contentType = "book" ' \
            'CREATE (b:booksOnly ' \
            '{name: n.name, referenceId: id(n), isbn: n.isbn})'
        self.gdb.query(q)

        if not self.suppress_output:
            print 'building relationships'

        # create relationships
        q = 'MATCH (n1:bookData) -- r -- n2, (b1:booksOnly), (b2:booksOnly) ' \
            'WHERE n1.contentType = "book" AND NOT r.contentType = "book" ' \
            'AND b1.referenceId = id(n1) AND b2.referenceId = id(n2) ' \
            'WITH n1, COLLECT(r) as rels, SUM(r.weight) as w, b1, b2 ' \
            'CREATE (b1) - [:Knows {weight: w}] -> (b2)'
        self.gdb.query(q)
        # TODO: this is creating duplicate relationships, and adding a
        # conditional to only pick nodes with no relationship isn't working
