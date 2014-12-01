from neo4jrestclient.client import GraphDatabase, Node
import csv
import json
import urllib2

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
        #TODO: create tag updater from library thing csv


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
                # non-list fields will not be matched
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
                continue

            if 'weight' in row:
                book.set('weight', row['weight'])
            if 'dimensions' in row:
                book.set('dimension', row['dimensions'])

            if 'originallanguage' in row:
                node = self.findOrCreateNode(row['originallanguage'][0], 'language', graphName)
                node.Knows(book)

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
                'tags':         5,
                'language':     6,
                'events':       7,
                'type':         8,
                'recommender':  8,
                'references':   8,
                'characters':   9,
                'author':       10
        }


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


