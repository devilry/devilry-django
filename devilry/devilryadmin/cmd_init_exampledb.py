#!/usr/bin/env python
# Clear and initialize exampledb. Creates a database with the standard users, but no other devilry data.

if __name__ == '__main__':
    from os import mkdir
    from os.path import exists
    from shutil import rmtree
    from common import require_djangoproject, depends, Command

    require_djangoproject()
    depends(Command('clear_exampledb'))

    if exists('deliverystore'):
        rmtree('deliverystore')
        print "Removed deliverystore/"
    mkdir('deliverystore')
