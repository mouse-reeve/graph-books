import csv
import urllib2
import neo4jrestclient.client as client
from neo4jrestclient.client import GraphDatabase
from dbTools import *

gdb = GraphDatabase("http://localhost:7474/db/data/")

url = 'https://raw.githubusercontent.com/mouse-reeve/book-catalogue/master/library.csv'
response = urllib2.urlopen(url)

reader = csv.DictReader(response)
for row in reader:

    # mandatory fields
    if 'title' in row:
        title = row['title']
    else:
        continue

    if 'isbn' in row:
        isbn = row['isbn']
    else:
        continue

    existing = findByISBN(isbn)
    if existing:
        # book is already in library
        continue

    book = gdb.node(name=title, isbn=isbn)
    book.labels.add('book')

    # additional info
    if 'format' in row:
        book.set('format', row['format'])
    if 'list_price' in row:
        book.set('price', row['list_price'])
    if 'description' in row:
        book.set('description', row['description'])
    if 'pages' in row:
        book.set('pageCount', row['pages'])

    # relationships
    if 'author_details' in row:
        # assumes the first author is canonical. will cause problems for
        # books with two distinct and legitimate authors (Good Omens), but
        # keeps out a ton of crap data
        author = row['author_details'].split('|')[0]
        firstName = author.split(', ')[1]
        lastName = author.split(', ')[0]
        params = {'type': 'author',
                  'anonymize': 0,
                  'firstName': firstName,
                  'lastName': lastName}
        buildRelationship(book, author, 'person', 'written by', params)
    if 'publisher' in row and row['publisher']:
        buildRelationship(book, row['publisher'], 'company', 'published by')
    if 'series_details' in row:
        series = row['series_details'].split('|')[0]
        series = series.split('(')[0].strip()
        if series:
            buildRelationship(book, series, 'series', 'part of the series')

