''' various algorithms and processes to run on the graph database '''

from neo4jrestclient.client import GraphDatabase
from datetime import datetime

import createGraphs
import prims
import depthFirstSearch
import simpleList


class DatabaseEditor(object):

    ''' updates and modifies the book database '''
    def __init__(self):
        self.creator = createGraphs.CreateGraphs()
        self.prims = prims.Prims()
        self.dfs = depthFirstSearch.DepthFirstSearch()
        self.simpleList = simpleList.SimpleList()

        self.gdb = GraphDatabase("http://localhost:7474/db/data/")

    def create_graphs(self):
        ''' create the base graph and books-only graph '''
        self.timed_run(self.creator.add_books)
        self.timed_run(self.creator.create_book_graph)

    def minimum_spanning_tree(self):
        ''' weighted tree based on book similarity '''
        # TODO: these aren't timed
        self.prims.minimum_spanning_tree('booksOnly', 'mstBooks')
        self.dfs.depth_first_search('mstBooks', 'dfsBookList')

    def simple_list(self, filename=None):
        ''' order books based on similarity '''
        # TODO: these aren't timed
        self.simpleList.simple_list('booksOnly', 'simpleBookList', filename)

    def timed_run(self, process):
        ''' print the runtime of a process '''
        start = datetime.now()
        process()
        end = datetime.now()
        runtime = end - start
        print 'process ran in %d seconds' % runtime.seconds
