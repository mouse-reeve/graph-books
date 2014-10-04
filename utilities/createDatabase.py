import csv
import neo4jrestclient.client as client
from neo4jrestclient.client import GraphDatabase
from dbTools import *

gdb = GraphDatabase("http://localhost:7474/db/data/")

fileName = 'library.csv'

with open(fileName, 'rb') as f:
    reader = csv.DictReader(f)
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
            buildRelationships(book, [author], 'person', 'written by', params)
        if 'publisher' in row and row['publisher']:
            buildRelationships(book, [row['publisher']], 'company', 'published by')
        if 'date_published' in row:
            # again, assuming a lot about good data format in my csv. oh well?
            year = row['date_published'][0:4]
            if year:
                buildRelationships(book, [year], 'year', 'published in', {'year': int(year)})
        if 'series_details' in row:
            series = row['series_details'].split('|')[0]
            series = series.split('(')[0].strip()
            if series:
                buildRelationships(book, [series], 'series', 'part of the series')

