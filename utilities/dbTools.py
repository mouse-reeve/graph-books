import csv
import neo4jrestclient.client as client
from neo4jrestclient.client import GraphDatabase

gdb = GraphDatabase("http://localhost:7474/db/data/")

# Creates a relationship between a book to all other books that share a given
# value for that field
def relateSharedField(book, field, value):
    # Find nodes with trait
    q = 'MATCH n WHERE "%s" IN n.%s RETURN n' % (value, field)
    print q
    try:
        str(value)
    except:
        return False
    if '"' in str(value):
        return False

    nodes = gdb.query(q, returns=(client.Node))
    for node in nodes:
        node = node[0]

        if node.id == book.id:
            continue

        if not len(node.relationships):
            print 'adding relationship to %s and %s' % (book.id, node.id)
            book.Knows(node, fields=[field], weight=1)
        else:
            exists = False
            existingRelationship = None
            dupe = False
            for rel in node.relationships:
                if field not in rel.properties['fields']\
                        and (rel.start.id == book.id or rel.end.id == book.id):
                    exists = True
                    existingRelationship = rel

                if field in rel.properties['fields']\
                        and (rel.start.id == book.id or rel.end.id == book.id):
                    dupe = True
                    break

            if not dupe:
                if exists:
                    fields = existingRelationship.properties['fields']
                    fields.append(field)

                    weight = existingRelationship.properties['weight'] + 1

                    existingRelationship.set('fields', fields)
                    existingRelationship.set('weight', weight);
                else:
                    book.Knows(node, fields=[field], weight=1)


def findByISBN(isbn):
    q = 'MATCH n WHERE n.isbn = "%s" RETURN n' % isbn
    nodes = gdb.query(q, returns=(client.Node))

    if len(nodes) > 0 and len(nodes[0]) > 0:
        return nodes[0][0]
    else:
        variant = isbn[0:-1]
        q = 'MATCH n WHERE n.isbn =~ ".*%s.*" RETURN n' % variant
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
            q = 'MATCH b WHERE b.name =~ "(?i)%s.*") RETURN b' % variant
            nodes = gdb.query(q, returns=(client.Node))
        except:
            print 'UNEXPECTED ERROR: query on title failed'
            return False

        if len(nodes) > 0:
            return nodes[0][0]
    print variants


def getAllBooks():
    # this will not work at scale.
    q = 'MATCH n RETURN n'
    nodes = gdb.query(q, returns=(client.Node))
    return nodes

