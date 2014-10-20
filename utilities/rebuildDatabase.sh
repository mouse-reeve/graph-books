neo4j stop
echo 'deleting database'
rm -rf /usr/local/Cellar/neo4j/2.1.3/libexec/data/graph.db
neo4j start
echo 'creating database. this could take a while'
python updateDatabase.py
echo 'tagging database. this could take a while'
python tagDatabase.py
