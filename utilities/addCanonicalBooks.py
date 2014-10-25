import csv
import urllib2
import neo4jrestclient.client as client
from neo4jrestclient.client import GraphDatabase
from dbTools import *

gdb = GraphDatabase("http://localhost:7474/db/data/")

url = 'https://raw.githubusercontent.com/mouse-reeve/book-catalogue/master/canonical.csv'
response = urllib2.urlopen(url)

reader = csv.DictReader(response)
for row in reader:
    # mandatory fields
    if 'title' in row and 'isbn' in row:
        title = row['title']
        isbn = row['isbn']
    else:
        continue

    existing = findByISBN(isbn)
    if existing:
        # book is already in library
        continue

    book = gdb.node(name=title, isbn=isbn)
    book.labels.add('book')

    # non-list fields will not be matched
    if 'description' in row:
        book.set('description', row['description'])
    if 'pages' in row:
        book.set('pageCount', row['pages'])
    if 'list_price' in row:
        book.set('price', row['list_price'])
    if 'format' in row:
        book.set('format', row['format'])

    # list fields, will be matched
    if 'author_details' in row:
        author = row['author_details'].split('|')
        book.set('author', [author[0]])
    if 'publisher' in row and [row['publisher']]:
        book.set('publisher', [row['publisher']])
    if 'series_details' in row:
        series = row['series_details'].split('|')[0]
        series = series.split('(')[0].strip()
        if len(series) > 0:
            book.set('series', [series])

