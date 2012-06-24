from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from devilry.apps.core.models import Subject, Period, Assignment
from django.db import connection


class Command(BaseCommand):
    help = 'tst'

    def handle(self, *args, **options):
        per = Assignment.objects.select_related('parentnode',
                                                'parentnode__parentnode',
                                                'parentnode__parentnode',
                                                'parentnode__parentnode__parentnode',
                                                'parentnode__parentnode__parentnode__parentnode',
                                                'parentnode__parentnode__parentnode__parentnode__parentnode').get(id=1)
        print per.short_name
        print per.parentnode.short_name
        print per.parentnode.parentnode.short_name
        print per.parentnode.parentnode.parentnode.short_name
        print per.parentnode.parentnode.parentnode.parentnode.short_name
        for qry in connection.queries:
            #print qry
            print '{sql} {time}'.format(**qry)
            print
        print
        print len(connection.queries)
