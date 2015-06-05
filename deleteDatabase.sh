#!/bin/bash
/Applications/neo4j-community-2.2.2/bin/neo4j stop
rm -rf /Applications/neo4j-community-2.2.2/data/*
/Applications/neo4j-community-2.2.2/bin/neo4j start
