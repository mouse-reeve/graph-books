''' run simple booklist sorting algorithm '''
from databaseEditor import DatabaseEditor
import sys

editor = DatabaseEditor()

editor.create_graphs()
editor.simple_list('booklist_%s' % sys.argv.pop())
