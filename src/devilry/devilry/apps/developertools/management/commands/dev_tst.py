from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from devilry.apps.core.models import Subject
from django.db import connection


class Command(BaseCommand):
    help = 'tst'

    def handle(self, *args, **options):
        items = Subject.objects.all()#.prefetch_related('admins__devilryuserprofile')
        for item in items:
            print item.short_name
            for admin in item.admins.all().prefetch_related('devilryuserprofile'):
                print admin.devilryuserprofile.full_name
        print
        for qry in connection.queries:
            print qry
            print '{sql} {time}'.format(**qry)
            print
        print
        print len(connection.queries)
