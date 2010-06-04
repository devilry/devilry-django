#!/bin/bash

rm -i db.sqlite3
python manage.py syncdb --noinput
python manage.py loaddata -v0 testusers
python manage.py loaddata -v0 testnodes
python manage.py loaddata -v0 testsubjects
python manage.py loaddata -v0 testperiods
python manage.py loaddata -v0 testassignments
python manage.py loaddata -v0 testassignmentgroups
