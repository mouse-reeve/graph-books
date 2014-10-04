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
            print 'creating new ' + createAs + ': ' + str(item)
        inputNode.relationships.create(relationship, node)

def findByISBN(isbn):
    q = 'MATCH (n {isbn: ' + str(isbn) + '}) RETURN n'

    nodes = gdb.query(q, returns=(client.Node))
    if len(nodes) > 0 and len(nodes[0]) > 0:
        return nodes[0][0]
    else:
        return false
