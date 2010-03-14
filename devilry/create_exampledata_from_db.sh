#!/bin/sh

python manage.py dumpdata core --indent=4 > core/fixtures/exampledata.json
python manage.py dumpdata grade_schema --indent=4 > core/fixtures/exampledata_schema.json
python manage.py dumpdata auth.user --indent=4 > core/fixtures/exampleusers.json
