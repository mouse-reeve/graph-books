import csv
import neo4jrestclient.client as client
from neo4jrestclient.client import GraphDatabase
from dbTools import *

gdb = GraphDatabase("http://localhost:7474/db/data/")

def buildRelationships(inputNode, items, createAs, relationship):
    for item in items:
        if type(item) is int:
            q = 'MATCH (n {name: ' + str(item) + '}) RETURN n'
        else:
            q = 'MATCH (n {name: "' + item + '"}) RETURN n'

        nodes = gdb.query(q, returns=(client.Node))
        if len(nodes) > 0 and len(nodes[0]) > 0:
            node = nodes[0][0]
        else:
            node = gdb.node(name=item)
            node.labels.add(createAs)
            #print 'creating new ' + createAs + ': ' + str(item)
        inputNode.relationships.create(relationship, node)

def findByISBN(isbn):
    q = 'MATCH (n {isbn: "' + str(isbn) + '"}) RETURN n'
    nodes = gdb.query(q, returns=(client.Node))

    if len(nodes) > 0 and len(nodes[0]) > 0:
        return nodes[0][0]
    else:
        return False

def findByTitle(title):
    if title.startswith('The '):
        title = title[4:] + ', ' + title[0:3]
    if title.startswith('A '):
        title = title[2:] + ', ' + title[0:1]

    title = title.split('(')[0]

    title = title.strip()

    try:
        q = 'START book=node(*) WHERE (book.name =~ "(?i)' + title + '") RETURN book'
        nodes = gdb.query(q, returns=(client.Node))
    except:
        print 'query on title failed'
        return False

    if len(nodes) > 0:
        return nodes[0][0]
    else:
        print title
        return False
