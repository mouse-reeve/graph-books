from neo4jrestclient.client import GraphDatabase
from datetime import datetime

import createGraphs
import prims
import depthFirstSearch
import simpleList


class DatabaseEditor:

    ''' updates and modifies the book database '''
    def __init__(self):
        self.creator = createGraphs.CreateGraphs()
        self.prims = prims.Prims()
        self.dfs = depthFirstSearch.DepthFirstSearch()
        self.simpleList = simpleList.SimpleList()

        self.gdb = GraphDatabase("http://localhost:7474/db/data/")

    def create_graphs(self):
        self.timed_run(self.creator.add_books)
        self.timed_run(self.creator.create_book_graph)

    def minimum_spanning_tree(self):
        # TODO: these aren't timed
        self.prims.minimum_spanning_tree('booksOnly', 'mstBooks')
        self.dfs.depth_first_search('mstBooks', 'dfsBookList')

    def simple_list(self):
        self.simpleList.simple_list('booksOnly', 'simpleBookList')

    def timed_run(self, process):
        start = datetime.now()
        process()
        end = datetime.now()
        runtime = end - start
        print 'process ran in %d seconds' % runtime.seconds
