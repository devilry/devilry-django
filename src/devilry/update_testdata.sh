#!/bin/sh

python manage.py dumpdata core --indent=4 > core/fixtures/testdata.json
python manage.py dumpdata auth.user --indent=4 > core/fixtures/testusers.json
