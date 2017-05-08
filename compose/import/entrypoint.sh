#!/bin/bash
# assuming initial django migrations for postgres have already been run


cd /code
sleep 15
python3 scripts/migrate_database.py

if [ ! -z "$MYSQL_DUMP" ]; then
    if [ -f "$MYSQL_DUMP" ]; then
        mysql_imports
    else
        echo "$MYSQL_DUMP is not an extant or readable file"
    fi
else
    echo "Variable MYSQL_DUMP unset or null"
fi

mysql_imports ()
{
    # entrypoint from mysql docker image.
    /entrypoint.sh mysqld &
    sleep 8
    echo "CREATE DATABASE cogat;" | mysql -u root
    mysql -u root < $MYSQL_DUMP
    python /code/scripts/mysql2neo.py
    python /code/scripts/user_import.py
}
