python manage.py dbdev_init && redis-server & /bin/sh docker/common/wait-for db:24376 -- DJANGOENV=test python manage.py test
