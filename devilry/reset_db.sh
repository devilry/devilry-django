#!/bin/bash

rm -i db.sqlite3
python manage.py syncdb --noinput
python manage.py loaddata -v0 exampleusers
python manage.py loaddata -v0 exampledata
python manage.py loaddata -v0 exampledata_schema
