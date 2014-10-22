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
        print bookData['isbn']

        if 'characters' in bookData:
            params = {'type': 'character', 'anonymize': 0}
            for character in bookData['characters']:
                try:
                    buildRelationship(book, character, 'person', 'has the character', params)
                except:
                    pass

        if 'places' in bookData:
            for place in bookData['places']:
                try:
                    buildRelationship(book, place, 'location', 'is set in')
                except:
                    pass

        if 'tags' in bookData:
            for tag in bookData['tags']:
                try:
                    buildRelationship(book, tag, 'concept', 'tagged as')
                except:
                    pass

        if 'purchasedAt' in bookData:
            for store in bookData['purchasedAt']:
                try:
                    buildRelationship(book, store, 'bookstore', 'purchased from')
                except:
                    pass

        if 'year' in bookData:
            try:
                year = int(bookData['year'])
                decade = (year/10)*10
                buildRelationship(book, str(year), 'year', 'first published in', {'year': year})
                buildRelationship(book, str(decade), 'year', 'from the decade', {'year': decade})
            except:
                pass


