from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from devilry.apps.administrator.simplified import *

class Command(BaseCommand):
    help = 'tst'

    def handle(self, *args, **options):
        grandma = User.objects.get(username='grandma')
        [x for x in SimplifiedAssignmentGroup.search(grandma,
                                                     filters=[{"field":"parentnode","comp":"exact","value":1}],
                                                     result_fieldgroups=["users", "feedback"])]
