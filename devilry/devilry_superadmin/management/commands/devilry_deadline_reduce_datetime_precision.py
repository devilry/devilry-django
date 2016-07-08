from django.db import transaction
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Set the microsecond of all deadlines to 0."

    def handle(self, *args, **kwargs):
        from devilry.apps.core.models import Deadline
        verbosity = int(kwargs.get('verbosity', '1'))

        updates = 0
        with transaction.commit_manually():
            for deadline in Deadline.objects.all():
                if deadline.deadline.microsecond != 0 and deadline.deadline.seconds != 0 and deadline.deadline.tzinfo != None:
                    deadline.deadline = Deadline.reduce_datetime_precision(deadline.deadline)
                    deadline.save()
                    if verbosity > 1:
                        print 'Updated deadline {0}'.format(deadline.id)
                elif verbosity > 1:
                    print 'Deadline {0} is already correctly formatted: {1}'.format(deadline.id, deadline.deadline)
                updates += 1
            transaction.commit()
        if verbosity > 0:
            print 'Successfully updated {0} deadlines.'.format(updates)
