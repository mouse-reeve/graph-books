import csv
import neo4jrestclient.client as client
from neo4jrestclient.client import GraphDatabase

gdb = GraphDatabase("http://localhost:7474/db/data/")

def buildRelationships(inputNode, items, createAs, relationship):
    for item in items:
        if type(item) is int:
            q = 'match (n {name: ' + str(item) + '}) return n'
        else:
            q = 'match (n {name: "' + item + '"}) return n'

        nodes = gdb.query(q, returns=(client.Node))
        if len(nodes) > 0 and len(nodes[0]) > 0:
            node = nodes[0][0]
        else:
            node = gdb.node(name=item)
            node.labels.add(createAs)
            print 'creating new ' + createAs + ': ' + str(item)
        inputNode.relationships.create(relationship, node)


fileName = 'books.csv'
if raw_input('use books.csv? ') == 'no':
    fileName = raw_input('Enter filename: ')

with open(fileName, 'rb') as f:
    reader = csv.DictReader(f)
    for row in reader:
        title = row["'TITLE'"]
        authorName = row["'AUTHOR (last, first)'"]
        isbn = row["'ISBNs'"]
        try:
            year = int(row["'DATE'"])
        except:
            year = 0
        tags = row["'TAGS'"]

        book = gdb.node(name=title, isbn=isbn, year=year)
        book.labels.add('Book')

        if tags and tags.split(','):
            buildRelationships(book, tags.split(','), 'Tag', 'tagged as')
        buildRelationships(book, [authorName], 'Person', 'written by')
        buildRelationships(book, [year], 'Year', 'published in')


