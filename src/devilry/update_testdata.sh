#!/bin/sh

python manage.py dumpdata core --indent=4 > core/fixtures/testdata.json
