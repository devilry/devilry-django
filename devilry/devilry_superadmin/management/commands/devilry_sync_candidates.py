from django.db import transaction
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Sync the cached fields in Candidate with the actual data from User."

    def handle(self, *args, **kwargs):
        from devilry.apps.core.models import Candidate

        verbosity = int(kwargs.get('verbosity', '1'))

        updates = 0
        with transaction.commit_manually():
            for candidate in Candidate.objects.all():
                candidate.save()
                if verbosity > 1:
                    print 'Updated {0}'.format(candidate)
                updates += 1
            transaction.commit()
        if verbosity > 0:
            print 'Successfully updated {0} candidates.'.format(updates)
