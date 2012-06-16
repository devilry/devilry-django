from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from devilry.apps.core.models import Assignment
from django.db import connection


class Command(BaseCommand):
    help = 'tst'

    def handle(self, *args, **options):
        items = Assignment.objects.all().prefetch_related('admins__devilryuserprofile')
        for item in items:
            print item.short_name
        print
        for qry in connection.queries:
            #print '{time:<10}: {sql}'.format(**qry)
            print '{sql} {time}'.format(**qry)
            print
        print
        print len(connection.queries)
