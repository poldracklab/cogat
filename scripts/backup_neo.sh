#!/bin/bash
set -ex
BACKUP_DIR=/backup/$(date +%s) 
NEO_BACKUP=/var/lib/neo4j-enterprise-2.3.11/bin/neo4j-backup
CONTAINER_ID=$(docker ps -qf "name=graphdb_ro")
docker exec -it $CONTAINER_ID $NEO_BACKUP -host graphdb -to $BACKUP_DIR -full
