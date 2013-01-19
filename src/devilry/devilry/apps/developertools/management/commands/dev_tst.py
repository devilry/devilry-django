from django.core.management.base import BaseCommand
from haystack.query import SearchQuerySet
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'tst'

    def handle(self, *args, **options):
        thor = User.objects.get(username='thor')
        results = SearchQuerySet().filter(admins=thor.id).auto_query('duck1010')
        for result in results:
            admin_ids = map(int, result.admins)
            admins = User.objects.filter(id__in=admin_ids)
            print thor in admins, result.object.get_path()