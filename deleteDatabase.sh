#!/bin/bash
/Applications/neo4j-community-2.1.5/bin/neo4j stop
rm -rf /Applications/neo4j-community-2.1.5/data/*
/Applications/neo4j-community-2.1.5/bin/neo4j start
