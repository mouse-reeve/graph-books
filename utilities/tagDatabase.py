import csv
import neo4jrestclient.client as client
from neo4jrestclient.client import GraphDatabase
from dbTools import *

gdb = GraphDatabase("http://localhost:7474/db/data/")

fileName = 'libraryThing.csv'

attempts = 0
success = 0

with open(fileName, 'rb') as f:
    reader = csv.DictReader(f)
    for row in reader:
        attempts += 1
        isbn = row["'ISBNs'"]
        # this isn't great, but it works
        isbn = isbn[1:len(isbn)-1]
        if not isbn:
            continue

        book = findByISBN(isbn)
        if not book:
            book = findByTitle(row["'TITLE'"])

        if not book:
            continue

        tags = row["'TAGS'"]
        if tags and tags.split(','):
            success += 1
            buildRelationships(book, tags.split(','), 'concept', 'tagged as')
        else:
            print 'no tags - failed to tag ' + row["'TITLE'"]

print 'successful updates: %d' % success
print 'total attempts: %d' % attempts
print 'Success rate: ' + str(float(success)/float(attempts)*100) + '%'

