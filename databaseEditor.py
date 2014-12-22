from neo4jrestclient.client import GraphDatabase, Node
import csv
import json
import urllib2
import math


class DatabaseEditor:

    ''' updates and modifies the book database '''
    def __init__(self):
        github_url = 'https://raw.githubusercontent.com/mouse-reeve'
        self.canonical_csv = github_url + \
            '/book-catalogue/master/canonical.csv'
        self.lt_json = github_url + '/book-catalogue/master/librarything.json'
        self.lt_scraped = github_url + '/book-scraper/master/items.json'

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
            book = self.find_by_isbn(row['isbn'], graph_name)
            if not book:
                book = self.create_node(name, 'book', graph_name)
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
                        node = self.find_or_create_node(author, 'author',
                                                        graph_name)
                        node.Knows(book)
                if 'series_details' in row:
                    series = row['series_details'].split('|')[0]
                    series = series.split('(')[0].strip()
                    if len(series) > 0:
                        node = self.find_or_create_node(series, 'series',
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

            book = self.find_by_isbn(graph_name, isbns[0])
            if not book:
                book = self.find_by_title(name, graph_name)
                if not book:
                    print 'BOOK NOT FOUND'
                    print name
                    continue

            if 'weight' in row:
                book.set('weight', row['weight'])
            if 'dimensions' in row:
                book.set('dimension', row['dimensions'])

            if 'fromwhere' in row:
                node = self.find_or_create_node(row['fromwhere'],
                                                'purchasedAt', graph_name)
                node.Knows(book)

            if 'tags' in row:
                for tag in row['tags']:
                    parts = tag.split(':')
                    if len(parts) == 2:
                        if parts[0] == 'REFERENCES':
                            isbn = parts[1]
                            node = self.find_by_isbn(isbn, graph_name)
                            node.Knows(book)
                        elif parts[0] == 'RECOMMENDER':
                            node = self.find_or_create_node(parts[1],
                                                            'recommender',
                                                            graph_name)
                            node.Knows(book)
                        elif parts[0] == 'TYPE':
                            node = self.find_or_create_node(parts[1],
                                                            'type', graph_name)
                            node.Knows(book)
                    else:
                        node = self.find_or_create_node(tag, 'tags',
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
            book = self.find_by_isbn(isbn, graph_name)
            if not book:
                print 'BOOK NOT FOUND: %s' % datum
                continue

            for field in datum:
                if not len(datum[field]):
                    continue

                if isinstance(datum[field], list):
                    for item in datum[field]:
                        node = self.find_or_create_node(item, field,
                                                        graph_name)
                        node.Knows(book)
                else:
                    if field == 'year':
                        try:
                            num_year = int(datum['year'])
                            decade = str(int(math.floor(num_year / 10) * 10))
                            node = self.find_or_create_node(decade, 'decade',
                                                            graph_name)
                            node.Knows(book)
                        except:
                            print 'failed to create decade for year %s' % \
                                  datum['year']
                            pass
                    node = self.find_or_create_node(datum[field], field,
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
            'recommender':  8,
            'references':   8,
            'characters':   9,
            'author':       10,
            'type':         15
        }

        q = 'MATCH (n:bookData) WHERE n.contentType = "book" ' \
            'CREATE (b:booksOnly ' \
            '{name: n.name, referenceId: id(n), isbn: n.isbn}) RETURN b'
        # TODO: why am I doing this thing? it seems like not a good thing
        all_books = self.gdb.query(q, returns=Node)._elements

        while len(all_books):
            book = all_books.pop()[0]
            print 'working on %s' % book.properties['name']
            print len(all_books)
            for relatedBook in all_books:
                q = 'MATCH b1 -- n -- b2 ' \
                    'WHERE id(b1) = %d AND id(b2) = %d ' \
                    'AND NOT n.contentType = "book" ' \
                    'RETURN distinct n' % \
                    (book.properties['referenceId'],
                     relatedBook[0].properties['referenceId'])
                connections = self.gdb.query(q, returns=Node)

                weight = 0
                properties = []
                for connection in connections:
                    connection_type = connection[0].properties['contentType']
                    weight += 1  # weights[connection_type]
                    properties.append(connection_type + ':' +
                                      connection[0].properties['name'])

                if weight > 0:
                    book.knows(relatedBook[0], weight=weight,
                               sharedAttributes=', '.join(properties))

    '''
    Prim's algorithm (more or less)
    '''
    def minimal_spanning_tree(self):
        books_graph = 'booksOnly'
        mst_graph = 'mstBooks'
        q = 'MATCH (n:%s) SET n.weight = 0, n.available = True, ' \
            'n.mstNodeId = ""' % books_graph
        self.gdb.query(q)

        # start with the True Confessions of Charlotte Doyle, obvi
        q = 'MATCH (n:%s) WHERE n.isbn = "9780380714759" ' \
            'SET n.weight = 1' % books_graph
        self.gdb.query(q)

        while True:
            # Find the weightiest available node. just picking the first node.
            q = 'MATCH (n:%s) WHERE n.weight > 0 AND n.available ' \
                'RETURN n ORDER BY n.weight DESC limit 1' % books_graph
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
                'ORDER BY r.weight DESC limit 1' % (books_graph, node.id)
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

                print '%s -> %s' % (connector_node.properties['name'],
                                    node.properties['name'])

            # these two nodes will reference each other
            node.set('available', False)
            mst_node = self.gdb.node(name=node.properties['name'],
                                     isbn=node.properties['isbn'],
                                     weight=weight)
            mst_node.labels.add(mst_graph)
            node.set('mstNodeId', mst_node.id)

            if connector_node:
                mst_node.nows(connector_node)

            # re-weight all the nodes
            q = 'MATCH n - [r] - b ' \
                'WHERE id(n) = %d AND r.weight > b.weight ' \
                'SET b.weight = r.weight' % node.id
            self.gdb.query(q)

    # queries

    def create_node(self, name, content_type, graph_name):
        print 'creating node %s, type %s, in %s' % \
              (name, content_type, graph_name)
        node = self.gdb.node(name=name, contentType=content_type)
        node.labels.add(graph_name)
        return node

    def find_or_create_node(self, name, content_type, graph_name):
        name = name.replace('"', '')
        node = self.findByName(name, content_type, graph_name)
        if not node:
            node = self.create_node(name, content_type, graph_name)
        return node

    def find_by_isbn(self, isbn, graph_name):
        q = 'MATCH (n:%s) WHERE n.isbn = "%s" RETURN n' % (graph_name, isbn)
        nodes = self.gdb.query(q, returns=Node)

        if len(nodes) > 0 and len(nodes[0]) > 0:
            return nodes[0][0]
        else:
            # checks for alternate ISBN format used by LibraryThing
            variant = isbn[0:-1]
            q = 'MATCH (n:%s) WHERE n.isbn =~ ".*%s.*" RETURN n' % \
                (graph_name, variant)
            nodes = self.gdb.query(q, returns=Node)
            if len(nodes) > 0 and len(nodes[0]) > 0:
                return nodes[0][0]
        return False

    def find_by_title(self, title, graph_name):
        q = 'MATCH (b:%s) WHERE b.name =~ "(?i).*%s.*" RETURN b' % \
            (graph_name, title)
        nodes = self.gdb.query(q, returns=Node)
        if len(nodes) > 0 and len(nodes[0]) > 0:
            return nodes[0][0]
        return False
