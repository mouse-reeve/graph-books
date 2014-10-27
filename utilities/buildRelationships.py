from neo4jrestclient.client import GraphDatabase
from dbTools import *

gdb = GraphDatabase("http://localhost:7474/db/data/")

books = getAllBooks()

beenThere = []

for book in books:
    book = book[0]
    print 'Working on %d' % book.id
    for field in book.properties:
        # ignore empty and non-list fields
        if not len(book.properties[field]) or\
                not isinstance(book.properties[field], list):
            continue

        for value in book.properties[field]:
            try:
                if '"' in str(value):
                    continue
            except:
                continue

            fieldName = '%s:%s' % (field, str(value))
            if not fieldName in beenThere:
                beenThere.append(fieldName)
                relateSharedField(field, value)

