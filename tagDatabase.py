import csv
import neo4jrestclient.client as client
from neo4jrestclient.client import GraphDatabase
from dbTools import *

gdb = GraphDatabase("http://localhost:7474/db/data/")

fileName = 'libraryThing.csv'

with open(fileName, 'rb') as f:
    reader = csv.DictReader(f)
    for row in reader:
        isbn = row["'ISBNs'"]
        # this isn't great, but it works
        isbn = isbn[1:len(isbn)-1]
        if not isbn:
            continue

        tags = row["'TAGS'"]

        book = findByISBN(isbn)

        if book and tags and tags.split(','):
            buildRelationships(book, tags.split(','), 'tag', 'tagged as')


