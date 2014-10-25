import neo4jrestclient.client as client
from neo4jrestclient.client import GraphDatabase
from dbTools import *

gdb = GraphDatabase("http://localhost:7474/db/data/")

books = getAllBooks()

for book in books:
    book = book[0]
    for field in book.properties:
        # ignore empty and non-list fields
        if not len(book.properties[field]) or\
                not isinstance(book.properties[field], list):
            continue

        for value in book.properties[field]:
            relateSharedField(book, field, value)

