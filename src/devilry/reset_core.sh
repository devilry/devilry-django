#!/bin/bash

python manage.py sqlreset core |sqlite3 db.sqlite3 
