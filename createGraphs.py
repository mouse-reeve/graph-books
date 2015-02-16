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
        self.canonical_csv = github_url + \
            '/book-catalogue/master/canonical.csv'
        self.lt_json = github_url + '/book-catalogue/master/librarything.json'
        self.lt_scraped = github_url + '/book-scraper/master/items.json'

        self.suppress_output = False

        self.utils = utilities.Utilities()

        self.gdb = GraphDatabase("http://localhost:7474/db/data/")

    def add_books(self):
        graph_name = 'bookData'
        self.add_canonical_data(graph_name)
        self.add_library_thing_data(graph_name)
        self.add_scraped_data(graph_name)

    def add_canonical_data(self, graph_name):
        response = urllib2.urlopen(self.canonical_csv)
        reader = csv.DictReader(response)

        for row in reader:
            if 'title' not in row or 'isbn' not in row:
                continue
            name = row['title'].replace('"', '')
            book = self.utils.find_by_isbn(row['isbn'], graph_name)
            if not book:
                book = self.utils.create_node(name, 'book', graph_name)
                book.set('isbn', row['isbn'])
                if 'description' in row:
                    book.set('description', row['description'])
                if 'pages' in row:
                    book.set('pageCount', row['pages'])
                if 'list_price' in row:
                    book.set('price', row['list_price'])
                if 'format' in row:
                    book.set('format', row['format'])
                if 'publisher' in row and [row['publisher']]:
                    book.set('publisher', row['publisher'])

                if 'author_details' in row:
                    authors = row['author_details'].split('|')
                    for author in authors:
                        node = self.utils.find_or_create_node(author, 'author',
                                                              graph_name)
                        node.Knows(book)
                if 'series_details' in row:
                    series = row['series_details'].split('|')[0]
                    series = series.split('(')[0].strip()
                    if len(series) > 0:
                        node = self.utils.find_or_create_node(series, 'series',
                                                              graph_name)
                        node.Knows(book)

    def add_library_thing_data(self, graph_name):
        # download libraryThing json export
        response = urllib2.urlopen(self.lt_json)
        data = json.load(response)

        for datum in data:
            row = data[datum]
            if 'isbn' not in row or 'title' not in row:
                continue

            try:
                isbns = row['isbn'].values()
            except:
                continue

            name = row['title']
            book = self.utils.find_by_isbn(isbns[0], graph_name)
            if not book:
                book = self.utils.find_by_title(name, graph_name)
                if not book:
                    if not self.suppress_output:
                        print 'BOOK NOT FOUND'
                        print name
                    continue

            if 'weight' in row:
                book.set('weight', row['weight'])
            if 'dimensions' in row:
                book.set('dimension', row['dimensions'])

            if 'fromwhere' in row:
                node = self.utils.find_or_create_node(row['fromwhere'],
                                                      'purchasedAt',
                                                      graph_name)
                node.Knows(book)

            if 'tags' in row:
                for tag in row['tags']:
                    parts = tag.split(':')
                    if len(parts) == 2:
                        if parts[0] == 'REFERENCES':
                            isbn = parts[1]
                            node = self.utils.find_by_isbn(isbn, graph_name)
                        else:
                            node = self\
                                .utils.find_or_create_node(parts[1],
                                                           parts[0].lower(),
                                                           graph_name)
                    else:
                        node = self.utils.find_or_create_node(tag, 'tags',
                                                              graph_name)
                    node.Knows(book)

    def add_scraped_data(self, graph_name):
        # download libraryThing scraped data
        response = urllib2.urlopen(self.lt_scraped)
        data = json.load(response)

        for datum in data:
            if 'isbn' not in datum:
                continue
            isbn = datum['isbn']
            book = self.utils.find_by_isbn(isbn, graph_name)
            if not book:
                if not self.suppress_output:
                    print 'BOOK NOT FOUND: %s' % datum
                continue

            for field in datum:
                if not len(datum[field]):
                    continue

                if isinstance(datum[field], list):
                    for item in datum[field]:
                        node = self.utils.find_or_create_node(item, field,
                                                              graph_name)
                        node.Knows(book)
                else:
                    if field == 'year':
                        try:
                            num_year = int(datum['year'])
                            decade = str(int(math.floor(num_year / 10) * 10))
                            node = self.utils.find_or_create_node(decade,
                                                                  'decade',
                                                                  graph_name)
                            node.Knows(book)
                        except:
                            if not self.suppress_output:
                                print 'failed to create decade for year %s' % \
                                      datum['year']
                            pass
                    node = self.utils.find_or_create_node(datum[field], field,
                                                          graph_name)
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
            'events':       7,
            'tags':         7,
            'type':         7,
            'readability':  7,
            'recommender':  8,
            'references':   8,
            'characters':   9,
            'author':       10,
            'mood':         12
        }

        # weight all non-book nodes (currently, sets all weights to 1)
        if not self.suppress_output:
            print 'adding weights to book data graph'
        for (weight, field) in enumerate(weights):
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
