from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from devilry.apps.core.models import Subject, Period, Assignment, AssignmentGroup
from django.db import connection


class Command(BaseCommand):
    help = 'tst'

    def handle(self, *args, **options):
        groups = AssignmentGroup.objects.prefetch_related('deadlines').all()[:3]
        for g in groups:
            print g.name
            print g.deadlines.all()
        for qry in connection.queries:
            #print qry
            print '{sql} {time}'.format(**qry)
            print
        print
        print len(connection.queries)
