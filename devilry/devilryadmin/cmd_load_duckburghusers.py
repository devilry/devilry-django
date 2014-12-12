#!/usr/bin/env python
# Load duckburgh users into the current database. All of them has "test" as password.

if __name__ == '__main__':
    from common import require_djangoproject, load_devilryadmin_fixture

    require_djangoproject()
    load_devilryadmin_fixture('duckburghusers.json')
