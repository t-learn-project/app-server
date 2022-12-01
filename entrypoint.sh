#!/bin/sh

if [ "$TLEARN_DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $TLEARN_DATABASE_HOST $TLEARN_DATABASE_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL ready"
fi

# python manage.py flush --no-input
python manage.py migrate
python manage.py collectstatic

exec "$@"