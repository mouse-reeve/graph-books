graph-books
===========

A graph representation of my library.

The `bookData` graph stores a node for each book (identified by isbn number), and a linked node for each piece of information about that book. 

`booksOnly` contains only the book nodes, and weights the relationships between any two books as the sum of the weighted values of all the non-book nodes that those two book nodes share in the `bookData` graph.
