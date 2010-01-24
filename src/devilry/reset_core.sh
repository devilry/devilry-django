#!/bin/bash

rm -i db.sqlite3
python manage.py syncdb --noinput
python manage.py loaddata -v0 testusers
python manage.py loaddata -v0 testdata
