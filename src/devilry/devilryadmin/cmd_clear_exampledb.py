#!/usr/bin/env python
# Clear example DB.

if __name__ == '__main__':
    from os import remove
    from os.path import exists
    from subprocess import call
    from common import require_djangoproject

    require_djangoproject()
    if exists('db.sqlite3'):
        remove('db.sqlite3')
        print "Removed db.sqlite"
    print "Syncing DB"
    call(['python', 'manage.py', 'syncdb', '--noinput', '-v0'])
    print "Database is now clean."
    print "Use 'python manage.py loaddata' to load fixtures into the empty database. Example:"
    print "   ~# python manage.py loaddata simplified/fixtures/simplified/*.json"
    print
