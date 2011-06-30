#!/usr/bin/env python
# Load the grandma user (a superuser) into the current database. She uses "test" as her password.

if __name__ == '__main__':
    from common import require_djangoproject, load_devilryadmin_fixture

    require_djangoproject()
    load_devilryadmin_fixture('grandma.json')
