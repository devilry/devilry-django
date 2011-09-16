from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ValidationError

from devilry.apps.core.models import Subject, Period, RelatedExaminer
import sys


class RelatedBaseCommand(BaseCommand):
    args = '<subject short name> <period short name>'

    def get_course_and_period(self, args):
        """ Get the course and period from args """
        if len(args) != 2:
            raise CommandError('Subject and period is required. See --help.')
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

    def add_users(self, modelcls, args, options):
        """ Add the users read from stdin to the given relatedmanager
        """
        self.verbosity = int(options.get('verbosity', '1'))
        lines = sys.stdin.readlines()
        modelcls.objects.filter(period=self.period).delete() # clear current values
        #relatedmanager.filter(period=self.period).delete() # clear current values
        for userspec in lines:
            userspec = userspec.strip()
            rel = modelcls(period=self.period, username=userspec)
            try:
                rel.clean()
            except ValidationError, e:
                raise CommandError('Invalid user spec: "{0}": {1}'.format(userspec.encode(sys.stdout.encoding), e.messages[0]))
            rel.save()
            if self.verbosity > 1:
                print "Added {0}: \"{1}\"".format(self.user_type, userspec.encode(sys.stdout.encoding))
        if self.verbosity > 0:
            print "Added {0} related {1}s to {2}.{3}".format(len(lines),
                                                             self.user_type,
                                                             args[0], args[1])
            

class Command(RelatedBaseCommand):
    help = 'Set related examiners on a period. Usernames are read from stdin, one username on each line.'
    user_type = "examiner"

    def handle(self, *args, **options):
        self.get_course_and_period(args)
        self.add_users(RelatedExaminer, args, options)
