neo4j stop
echo 'deleting database'
rm -rf /usr/local/Cellar/neo4j/2.1.3/libexec/data/graph.db
neo4j start
echo 'adding books to database. this could take a while'
python addCanonicalBooks.py
echo 'adding LibraryThing data to books. this will absolutely take a while'
python addLibraryThingData.py
echo 'building relationships between books. Again, be patient.'
python buildRelationships.py
