import csv
import neo4jrestclient.client as client
from neo4jrestclient.client import GraphDatabase

gdb = GraphDatabase("http://localhost:7474/db/data/")

def buildRelationship(inputNode, item, label, relationship, params={}):
    if type(item) is int:
        q = 'MATCH (n:%s {name: %d}) RETURN n' % (label, item)
    else:
        q = 'MATCH (n:%s {name: "%s"}) RETURN n' % (label, item)

    nodes = gdb.query(q, returns=(client.Node))
    if len(nodes) > 0 and len(nodes[0]) > 0:
        node = nodes[0][0]
    else:
        node = gdb.node(name=item)
        node.labels.add(label)
        for key, value in params.iteritems():
            node.set(key, value)
        print 'creating new ' + label + ': ' + str(item)

    relationships = inputNode.relationships.all()
    for rel in relationships:
        if node.id == rel.end.id:
            return
    inputNode.relationships.create(relationship, node)

def findByISBN(isbn):
    q = 'MATCH (n {isbn: "' + str(isbn) + '"}) RETURN n'
    nodes = gdb.query(q, returns=(client.Node))

    if len(nodes) > 0 and len(nodes[0]) > 0:
        return nodes[0][0]
    else:
        variant = isbn[0:-1]
        q = 'MATCH (b:book) WHERE (b.isbn =~ ".*' + variant +'.*") RETURN b'
        nodes = gdb.query(q, returns=(client.Node))
        if len(nodes) > 0 and len(nodes[0]) > 0:
            return nodes[0][0]
    return False

def findByTitle(title):
    title = title.strip()
    title = title.replace('&#039;', '\'')
    variants = [title]

    alternates = {
            '&': 'and',
            ' and ': ' & ',
            'Vol.': 'Volume',
            'Volume': 'Vol.'
            }

    for key, value in alternates.iteritems():
        variants.append(title.replace(key, value))

    extras = ['(', ':', '.', ';', ',']
    for delimiter in extras:
        cleaned = title.split(delimiter)[0].strip()
        if not cleaned in variants:
            variants.append(cleaned)

    starters = ['The ', 'A ', 'An ']
    for variant in variants:
        for word in starters:
            if variant.startswith(word):
                variants.append(variant[len(word):] + ', ' + variant[0:len(word)-1])
                variants.append(variant[len(word):])

    for variant in variants:
        try:
            q = 'MATCH (b:book) WHERE (b.name =~ "(?i)' + variant + '.*") RETURN b'
            nodes = gdb.query(q, returns=(client.Node))
        except:
            print 'UNEXPECTED ERROR: query on title failed'
            return False

        if len(nodes) > 0:
            return nodes[0][0]
    print variants

