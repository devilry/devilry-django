from django.contrib.auth import get_user_model
from django.db import transaction
from django.core.management.base import NoArgsCommand


class Command(NoArgsCommand):
    help = "Re-save all users. This is useful if you have any apps that listens for " \
           "post_save signals on User, such as 'devilry.apps.autoset_empty_email_by_username'."

    def handle_noargs(self, **options):
        verbosity = int(options.get('verbosity', '1'))

        updates = 0
        with transaction.commit_manually():
            for user in get_user_model().objects.all():
                user.save()
                if verbosity > 1:
                    print 'Saved {0}'.format(user)
                updates += 1
            transaction.commit()
        if verbosity > 0:
            print 'Successfully re-saved {0} users.'.format(updates)
