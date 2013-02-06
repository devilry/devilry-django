from django.db import transaction
from django.core.management.base import NoArgsCommand



class Command(NoArgsCommand):
    help = "Set the microsecond of all deadlines to 0."

    def handle_noargs(self, **options):
        from devilry.apps.core.models import Deadline
        verbosity = int(options.get('verbosity', '1'))

        updates = 0
        with transaction.commit_manually():
            for deadline in Deadline.objects.all():
                if deadline.deadline.microsecond != 0:
                    deadline.remove_microsec()
                    deadline.save()
                    if verbosity > 1:
                        print 'Updated deadline {0}'.format(deadline.id)
                elif verbosity > 1:
                    print 'Deadline {0} already has milliseconds==0'.format(deadline.id)
                updates += 1
                transaction.commit()
        if verbosity > 0:
            print 'Successfully updated {0} deadlines.'.format(updates)
