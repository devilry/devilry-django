from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from devilry.apps.administrator.simplified import *
from django.db import connection

class Command(BaseCommand):
    help = 'tst'

    def handle(self, *args, **options):
        grandma = User.objects.get(username='grandma')
        #[x for x in SimplifiedRelatedStudent.search(grandma)]
        #[x for x in SimplifiedAssignmentGroup.search(grandma,
                                                     #filters=[{"field":"parentnode","comp":"exact","value":1}],
                                                     #result_fieldgroups=["feedback"])]
        [x for x in SimplifiedCandidate.search(grandma,
                                               filters=[{"field":"assignment_group__parentnode__parentnode","comp":"exact","value":1}])]
        for qry in connection.queries:
            #print '{time:<10}: {sql}'.format(**qry)
            print '{sql}'.format(**qry)
            print
        print
        print len(connection.queries)
