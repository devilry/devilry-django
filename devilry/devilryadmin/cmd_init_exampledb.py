#!/usr/bin/env python
# Clear and initialize exampledb. Creates a database with the standard users, but no other devilry data.

if __name__ == '__main__':
    from os import mkdir
    from os.path import exists
    from subprocess import call
    from shutil import rmtree
    from common import require_djangoproject, depends

    require_djangoproject()
    depends('clear_exampledb')

    if exists('deliverystore'):
        rmtree('deliverystore')
        print "Removed deliverystore/"
    mkdir('deliverystore')

    # TODO: make this work outside projects/dev/
    call(['python', 'manage.py', 'loaddata', '-v0', 'fixtures/users.json'])
