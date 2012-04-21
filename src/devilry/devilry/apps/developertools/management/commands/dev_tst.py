from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import connection
from devilry.apps.subjectadmin.rest.group import GroupDao


class Command(BaseCommand):
    help = 'tst'

    def handle(self, *args, **options):
        grandma = User.objects.get(username='grandma')
        dao = GroupDao()
        dao.read(grandma, 1)
        print
        for qry in connection.queries:
            #print '{time:<10}: {sql}'.format(**qry)
            print '{sql} {time}'.format(**qry)
            print
        print
        print len(connection.queries)
