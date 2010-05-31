#!/bin/sh

python manage.py dumpdata core.node --indent=4 > core/fixtures/testnodes.json
python manage.py dumpdata core.subject --indent=4 > core/fixtures/testsubjects.json
python manage.py dumpdata auth.user --indent=4 > core/fixtures/testusers.json
