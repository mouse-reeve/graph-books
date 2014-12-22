from neo4jrestclient.client import GraphDatabase, Node
import csv
import json
import urllib2
import math

class DatabaseEditor:
    ''' updates and modifies the book database '''


    def __init__(self):
        githubBaseUrl = 'https://raw.githubusercontent.com/mouse-reeve'
        self.canonicalCSV = githubBaseUrl + '/book-catalogue/master/canonical.csv'
        self.libraryThingJSON = githubBaseUrl + '/book-catalogue/master/librarything.json'
        self.libraryThingScraped = githubBaseUrl + '/book-scraper/master/items.json'

        self.gdb = GraphDatabase("http://localhost:7474/db/data/")


    def addBooks(self):
        graphName = 'bookData'
        self.addCanonicalData(graphName)
        self.addLibraryThingData(graphName)
        self.addScrapedData(graphName)


    def addCanonicalData(self, graphName):
        response = urllib2.urlopen(self.canonicalCSV)
        reader = csv.DictReader(response)

        for row in reader:
            if not 'title' in row or not 'isbn' in row:
                continue
            name = row['title'].replace('"', '')
            book = self.findByName(name, 'book', graphName)
            if not book:
                book = self.createNode(name, 'book', graphName)
                if 'isbn' in row:
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
                        node = self.findOrCreateNode(author, 'author', graphName)
                        node.Knows(book)
                if 'series_details' in row:
                    series = row['series_details'].split('|')[0]
                    series = series.split('(')[0].strip()
                    if len(series) > 0:
                        node = self.findOrCreateNode(series, 'series', graphName)
                        node.Knows(book)


    def addLibraryThingData(self, graphName):
        # download libraryThing json export
        response = urllib2.urlopen(self.libraryThingJSON)
        data = json.load(response)

        for datum in data:
            row = data[datum]

            if not 'isbn' in row or not 'title' in row:
                continue

            try:
                isbns = row['isbn'].values()
            except:
                continue

            name = row['title']

            book = self.findByISBN(graphName, isbns[0])
            if not book:
                book = self.findByTitle(name, graphName)
                if not book:
                    print 'BOOK NOT FOUND'
                    print name
                    continue

            if 'weight' in row:
                book.set('weight', row['weight'])
            if 'dimensions' in row:
                book.set('dimension', row['dimensions'])

            # TODO: this data is total crap.
            #if 'originallanguage' in row:
            #    node = self.findOrCreateNode(row['originallanguage'][0], 'language', graphName)
            #    node.Knows(book)

            if 'fromwhere' in row:
                node = self.findOrCreateNode(row['fromwhere'], 'purchasedAt', graphName)
                node.Knows(book)

            if 'tags' in row:
                for tag in row['tags']:
                    parts = tag.split(':')
                    if len(parts) == 2:
                        if parts[0] == 'REFERENCES':
                            isbn = parts[1]
                            node = self.findByISBN(graphName, isbn)
                            node.Knows(book)
                        elif parts[0] == 'RECOMMENDER':
                            node = self.findOrCreateNode(parts[1], 'recommender', graphName)
                            node.Knows(book)
                        elif parts[0] == 'TYPE':
                            node = self.findOrCreateNode(parts[1], 'type', graphName)
                            node.Knows(book)
                    else:
                        node = self.findOrCreateNode(tag, 'tags', graphName)
                        node.Knows(book)


    def addScrapedData(self, graphName):
        # download libraryThing scraped data
        response = urllib2.urlopen(self.libraryThingScraped)
        data = json.load(response)

        # hacky fix for redundant scraped data
        ignoreFields = ['purchasedAt', 'isbn', 'tags']

        for datum in data:
            if not 'isbn' in datum:
                continue
            isbn = datum['isbn']
            book = self.findByISBN(graphName, isbn)
            if not book:
                print 'BOOK NOT FOUND: %s' % datum
                continue

            for field in datum:
                if any(field in f for f in ignoreFields) or not len(datum[field]):
                    continue

                if isinstance(datum[field], list):
                    for item in datum[field]:
                        node = self.findOrCreateNode(item, field, graphName)
                        node.Knows(book)
                else:
                    if field == 'year':
                        try:
                            numYear = int(datum['year'])
                            decade = str(int(math.floor(numYear / 10) * 10))
                            node = self.findOrCreateNode(decade, 'decade', graphName)
                            node.Knows(book)
                        except:
                            print 'failed to create decade for year %s' % datum['year']
                            pass
                    node = self.findOrCreateNode(datum[field], field, graphName)
                    node.Knows(book)


    def createBookGraph(self):
        graphName = 'booksOnly'
        weights = {
                'publisher':    1,
                'purchasedAt':  2,
                'series':       3,
                'year':         4,
                'places':       5,
                'language':     6,
                'events':       7,
                'decade':       7,
                'tags':         7,
                'type':         8,
                'recommender':  8,
                'references':   8,
                'characters':   9,
                'author':       10
        }

        # this seems messy/problematic, but it should work.
        # leaving it outside a function since it's so specific
        q = 'MATCH (n:bookData) WHERE n.contentType="book" CREATE (b:booksOnly {name: n.name, referenceId: id(n), isbn: n.isbn}) RETURN b'
        allBooks = self.gdb.query(q, returns=Node)._elements

        while len(allBooks):
            book = allBooks.pop()[0]
            print 'working on %s' % book.properties['name']
            print len(allBooks)
            for relatedBook in allBooks:
                connections = self.getConnectionNodes(book.properties['referenceId'], relatedBook[0].properties['referenceId'])
                weight = 0
                properties = []
                for connection in connections:
                    connectionType = connection[0].properties['contentType']
                    weight += weights[connectionType]
                    properties.append(connectionType + ':' + connection[0].properties['name'])

                if weight > 0:
                    book.knows(relatedBook[0], weight=weight, sharedAttributes=', '.join(properties))


    def minimalSpanningTree(self):
        booksGraph = 'booksOnly'
        mstGraph = 'mstBooks'
        q = 'MATCH (n:%s) SET n.weight = 0, n.available = True, n.mstNodeId = ""' % booksGraph
        self.gdb.query(q)

        # start with the True Confessions of Charlotte Doyle, obvi
        q = 'MATCH (n:%s) WHERE n.isbn="9780380714759" SET n.weight=1' % booksGraph
        self.gdb.query(q)

        areNodesAvailable = True
        while areNodesAvailable:
            print 'FINDING available nodes by weight'

            # just picking the first node. Probs not ideal
            q = 'MATCH (n:%s) WHERE n.weight > 0 AND n.available RETURN n ORDER BY n.weight DESC limit 1' % booksGraph
            nodes = self.gdb.query(q, returns=Node)

            if not len(nodes):
                areNodesAvailable = False
                break

            node = nodes[0][0]

            # find the heighest weighed node already in the mst graph
            connectorNode = None
            edges = node.relationships
            q = 'MATCH (n:%s) - [r] - b WHERE id(n)=%d AND NOT b.available RETURN b ORDER BY r.weight DESC limit 1' % (booksGraph, node.id)
            connectors = self.gdb.query(q, returns=Node)

            # if there's no connector node, it's HOPEFULLY ok
            if len(connectors) and len(connectors[0]):
                q = 'MATCH n - [r] - b WHERE id(n)=%d AND id(b)=%d RETURN r.weight' % (node.id, connectors[0][0].id)
                weight = self.gdb.query(q)[0][0]
                print 'found node with weight %d' % weight

                # get the equivalent node from the MST graph
                q = 'MATCH n WHERE id(n)=%d RETURN n' % connectors[0][0].properties['mstNodeId']
                nodes = self.gdb.query(q, returns=Node)
                connectorNode = nodes[0][0]
            else:
                print 'this had better be node 1'

            print 'CREATING the new MST node'
            # these two nodes will reference each other
            node.set('available', False)
            mstNode = self.gdb.node(name=node.properties['name'], isbn=node.properties['isbn'])
            mstNode.labels.add(mstGraph)
            node.set('mstNodeId', mstNode.id)

            if connectorNode:
                mstNode.nows(connectorNode)

            print 'REWEIGHTING all remaining nodes'
            q = 'MATCH n - [r] - b WHERE id(n)=%d AND r.weight > b.weight SET b.weight = r.weight' % node.id
            self.gdb.query(q)


# --------------------------- queries


    def getConnectionNodes(self, bookId1, bookId2):
        q = 'MATCH b1 -- n -- b2 WHERE id(b1)=%d AND id(b2)=%d AND NOT n.contentType="book" RETURN distinct n' % (bookId1, bookId2)
        nodes = self.gdb.query(q, returns=Node)
        return nodes


    def getNodeById(self, nodeId):
        q = "MATCH n WHERE id(n)=%d RETURN n" % nodeId
        nodes = self.gdb.query(q, returns=Node)
        if not nodes[0] or not nodes[0][0]:
            return False

        return nodes[0][0]


    def getAvailableNodes(self, graphName):
        q = 'MATCH (n:%s) WHERE n.weight>0' % graphName
        q += 'AND n.available RETURN n ORDER BY n.weight DESC'
        nodes = self.gdb.query(q, returns=Node)
        return nodes


    def findByName(self, name, contentType, graphName):
        q = 'MATCH (n:%s) WHERE n.contentType = "%s" AND n.name = "%s" RETURN n' % (graphName, contentType, name)
        nodes = self.gdb.query(q, returns=Node)
        if len(nodes) > 0 and len(nodes[0]) > 0:
            return nodes[0][0]
        return False


    def createNode(self, name, contentType, graphName):
        print 'creating node %s, type %s, in %s' % (name, contentType, graphName)
        node = self.gdb.node(name=name, contentType=contentType)
        node.labels.add(graphName)
        return node


    def findOrCreateNode(self, name, contentType, graphName):
        name = name.replace('"', '')
        node = self.findByName(name, contentType, graphName)
        if not node:
            node = self.createNode(name, contentType, graphName)
        return node


    def findByISBN(self, graphName, isbn):
        q = 'MATCH (n:%s) WHERE n.isbn = "%s" RETURN n' % (graphName, isbn)
        nodes = self.gdb.query(q, returns=Node)

        if len(nodes) > 0 and len(nodes[0]) > 0:
            return nodes[0][0]
        else:
            # checks for alternate ISBN format used by LibraryThing
            variant = isbn[0:-1]
            q = 'MATCH (n:%s) WHERE n.isbn =~ ".*%s.*" RETURN n' % (graphName, variant)
            nodes = self.gdb.query(q, returns=Node)
            if len(nodes) > 0 and len(nodes[0]) > 0:
                return nodes[0][0]
        return False


    def findByTitle(self, title, graphName):
        q = 'MATCH (b:%s) WHERE b.name =~ "(?i).*%s.*" RETURN b' % (graphName, title)
        nodes = self.gdb.query(q, returns=Node)
        if len(nodes) > 0 and len(nodes[0]) > 0:
            return nodes[0][0]
        return False


