import csv
import neo4jrestclient.client as client
from neo4jrestclient.client import GraphDatabase

gdb = GraphDatabase("http://localhost:7474/db/data/")

def buildRelationships(inputNode, items, createAs, relationship):
    for item in items:
        q = 'match (n {name: "' + item + '"}) return n'
        nodes = gdb.query(q, returns=(client.Node))
        if len(nodes) > 0 and len(nodes[0]) > 0:
            node = nodes[0][0]
        else:
            node = gdb.node(name=item)
            node.labels.add(createAs)
            print 'creating new ' + createAs + ': ' + item
        inputNode.relationships.create(relationship, node)


with open('books.csv', 'rb') as f:
    reader = csv.DictReader(f)
    for row in reader:
        title = row["'TITLE'"]
        authorName = row["'AUTHOR (last, first)'"]
        isbn = row["'ISBNs'"]
        year = row["'DATE'"]
        tags = row["'TAGS'"]

        book = gdb.node(title=title, isbn=isbn, year=year)
        book.labels.add('Book')

        if tags.split(','):
            buildRelationships(book, tags.split(','), 'Tag', 'tag')
        buildRelationships(book, [authorName], 'Author', 'author')


