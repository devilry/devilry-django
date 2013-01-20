from django.core.management.base import BaseCommand
from haystack.query import SearchQuerySet
from django.contrib.auth.models import User
from devilry.apps.core.models import AssignmentGroup


class Command(BaseCommand):
    help = 'tst'

    def handle(self, *args, **options):
        thor = User.objects.get(username='thor')
#        print thor.id
        results = SearchQuerySet().filter(admin_ids=thor.id).models(AssignmentGroup).auto_query('donald')
        for result in results:
#            admin_ids = map(int, result.admins)
#            admins = User.objects.filter(id__in=admin_ids)
#            print dir(result)
            print result.object, result.student_ids, result.model_name
            print result.text
#            print thor in admins, result.object.get_path()