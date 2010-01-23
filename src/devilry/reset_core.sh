#!/bin/bash

rm -i db.sqlite3
python manage.py syncdb --noinput
python manage.py loaddata testusers
python manage.py loaddata testdata

#python manage.py sqlreset core |sqlite3 db.sqlite3 
