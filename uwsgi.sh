#!/bin/bash
while ! nc -z graphdb 7474; do sleep 3; done

python /code/manage.py makemigrations
python /code/manage.py migrate
python /code/manage.py collectstatic --noinput
# Must be run manually, otherwise will redo each time docker-compose restart uwsgi
#python /code/scripts/migrate_database.py

if [ "$MAKE_DEFAULT_USER" = True ]; then
    ./manage.py shell < /code/scripts/create_superuser.py
fi

uwsgi --ini /code/uwsgi.ini
