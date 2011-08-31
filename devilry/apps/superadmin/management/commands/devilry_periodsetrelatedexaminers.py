from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from optparse import make_option

from devilry_usermod import UserModCommand
from devilry.apps.core.models import Subject, Period
import sys

class BaseCommand(UserModCommand):
    args = '<subject short name> <period short name>'

    def get_course_and_period(self, args):
        """ Get the course and period from args """
        if len(args) != 2:
            raise CommandError('Course and period is required. See --help.')
        course_short_name = args[0]
        period_short_name = args[1]
        # Get the course and period
        try:
            self.subject = Subject.objects.get(short_name=course_short_name)
        except Subject.DoesNotExist, e:
            raise CommandError('Subject with short name %s does not exist.' % course_short_name)
        try:
            self.period = Period.objects.get(short_name=period_short_name, parentnode=self.subject)
        except Period.DoesNotExist, e:
            raise CommandError('Period with short name %s does not exist.' % period_short_name)

    def add_users(self, relatedmanager, args, options):
        """ Add the users read from stdin to the given relatedmanager
        """
        self.verbosity = int(options.get('verbosity', '1'))
        self.related_users_count = 0
        usernames = sys.stdin.read().split()
        # clear current values
        relatedmanager.filter(period=self.period).delete()
        for username in usernames:
            try:
                User.objects.get(username=username)
                relatedmanager.create(period=self.period, username=username)
                self.related_users_count += 1
                if self.verbosity > 1:
                    print "Added %s %s" % (self.user_type, username)
            except User.DoesNotExist:
                pass
        if self.verbosity > 0:
            print "Added %d related %ss to %s" % (self.related_users_count, self.user_type, "%s.%s" % (args[0], args[1]))
            
class Command(BaseCommand):
    help = 'Set related examiners on a period. Usernames are read from stdin, one username on each line.'
    user_type = "examiner"

    def handle(self, *args, **options):
        self.get_course_and_period(args)
        self.add_users(self.period.relatedstudents, args, options)
