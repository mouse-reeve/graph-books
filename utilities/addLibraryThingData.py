import json
import urllib2
import neo4jrestclient.client as client
from neo4jrestclient.client import GraphDatabase
from dbTools import *

gdb = GraphDatabase("http://localhost:7474/db/data/")

url = 'https://raw.githubusercontent.com/mouse-reeve/book-scraper/master/items.json'
response = urllib2.urlopen(url)
data = json.load(response)

for bookData in data:
    if 'isbn' in bookData:
        isbn = bookData['isbn']
        book = findByISBN(isbn)

        if not book:
            print 'BOOK NOT FOUND: %s' % bookData
            continue

        for field in bookData:
            if not len(bookData[field]):
                continue

            if field == 'year':
                try:
                    year = int(bookData['year'])
                    decade = (year/10)*10

                    book.set('year', [year])
                    book.set('decade', [decade])
                except:
                    pass
            elif not field == 'isbn' and isinstance(bookData[field], list):
                book.set(field, bookData[field])

