import json

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ValidationError

from devilry.apps.core.models import Subject, Period, RelatedExaminer
import sys


class RelatedBaseCommand(BaseCommand):
    args = '<subject short name> <period short name>'

    def get_subject_and_period(self, args):
        """ Get the subject and period from args """
        if len(args) != 2:
            raise CommandError('Subject and period is required. See --help.')
        subject_short_name = args[0]
        period_short_name = args[1]
        # Get the subject and period
        try:
            self.subject = Subject.objects.get(short_name=subject_short_name)
        except Subject.DoesNotExist, e:
            raise CommandError('Subject with short name %s does not exist.' % subject_short_name)
        try:
            self.period = Period.objects.get(short_name=period_short_name, parentnode=self.subject)
        except Period.DoesNotExist, e:
            raise CommandError('Period with short name %s does not exist.' % period_short_name)

    def add_users(self, modelcls, args, options):
        """ Add the users read from stdin to the given relatedmanager
        """
        self.verbosity = int(options.get('verbosity', '1'))
        jsondata = sys.stdin.read()
        data = json.loads(jsondata)
        self.period.relatedstudent_set.filter()
        for kw in data:
            username = kw.pop('username')
            user = self._get_user(username)
            if not self._update_reluser(modelcls, user, kw):
                self._create_reluser(modelcls, user, kw)
        if self.verbosity > 0:
            print "Added/updated {0} related {1}s to {2}.{3}".format(len(data),
                                                                     self.user_type,
                                                                     args[0], args[1])

    def _update_reluser(self, modelcls, user, kw):
            try:
                reluser = modelcls.objects.get(period=self.period, user=user)
            except modelcls.DoesNotExist, e:
                return False
            else:
                for key, value in kw.iteritems():
                    setattr(reluser, key, value)
                self._save_reluser(reluser, 'Updated')
                return True

    def _create_reluser(self, modelcls, user, kw):
        reluser = modelcls(period=self.period, user=user, **kw)
        self._save_reluser(reluser, 'Added')

    def _save_reluser(self, reluser, mode):
        try:
            reluser.full_clean()
        except ValidationError, e:
            raise CommandError('Invalid related user: "{0}"'.format(reluser))
        else:
            reluser.save()
            if self.verbosity > 1:
                print "{0} {1} {2}".format(mode, self.user_type, reluser)


    def _get_user(self, username):
            try:
                user = User.objects.get(username=username)
                return user
            except User.DoesNotExist, e:
                raise CommandError('User {0} does not exists', username)



class Command(RelatedBaseCommand):
    help = 'Set related examiners on a period. Users are read from stdin, as a JSON encoded array of arguments to the RelatedExaminer model. See devilry/apps/superadmin/examples/relatedexaminers.json for an example.'
    user_type = "examiner"

    def handle(self, *args, **options):
        self.get_subject_and_period(args)
        self.add_users(RelatedExaminer, args, options)
