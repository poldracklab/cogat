#! /bin/bash
if [[ ! -v COGAT_TESTING ]]; then
    /var/lib/neo4j/bin/neo4j console &
    sleep 6
    python scripts/migrate_database.py
fi
