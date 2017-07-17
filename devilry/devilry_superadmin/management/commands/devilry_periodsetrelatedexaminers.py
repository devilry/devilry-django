import json
from optparse import make_option

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ValidationError

import sys


class RelatedBaseCommand(BaseCommand):
    args = '<subject short name> <period short name>'
    option_list = BaseCommand.option_list + (
        make_option('--clearall',
            action='store_true',
            dest='clearall',
            default=False,
            help='Clear all related students on the period before adding.'),
        make_option('--removemissing',
                    action='store_true',
                    dest='removemissing',
                    default=False,
                    help='Remove all related students not in the JSON before updating.'),
        make_option('--smartmergetags',
                    action='store_true',
                    dest='smartmergetags',
                    default=False,
                    help='Do not remove existing tags, but add any new tags in the JSON.'),
    )

    def get_subject_and_period(self, args):
        """ Get the subject and period from args """
        from devilry.apps.core.models import Subject, Period
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
        if options.get('removemissing') and options.get('clearall'):
            raise CommandError('Use either --removemissing or --clearall, not both!')

        if options.get('removemissing'):
            self._remove_related_users_not_in_json(modelcls, data=data)
        elif options.get('clearall'):
            self._clearAllRelatedOnPeriod(modelcls)

        for kw in data:
            username = kw.pop('username')
            user = self._get_user(username)
            if not self._update_reluser(modelcls, user, kw, smart_merge_tags=options.get('smartmergetags')):
                self._create_reluser(modelcls, user, kw)
        if self.verbosity > 0:
            print "Added/updated {0} related {1}s to {2}.{3}".format(len(data),
                                                                     self.user_type,
                                                                     args[0], args[1])

    def _clearAllRelatedOnPeriod(self, modelcls):
        modelcls.objects.filter(period=self.period).delete()
        if self.verbosity > 0:
            print "Removed all related students in: {0}".format(self.period)

    def _remove_related_users_not_in_json(self, modelcls, data):
        usernames = [item['username'] for item in data]
        modelcls.objects\
            .filter(period=self.period)\
            .exclude(user__username__in=usernames)\
            .delete()
        if self.verbosity > 0:
            print "Removed related users in JSON: {0}".format(usernames)

    def _update_reluser(self, modelcls, user, kw, smart_merge_tags):
            try:
                reluser = modelcls.objects.get(period=self.period, user=user)
            except modelcls.DoesNotExist, e:
                return False
            else:
                old_tags = reluser.tags
                for key, value in kw.iteritems():
                    setattr(reluser, key, value)
                if smart_merge_tags and old_tags:
                    new_tags = kw.get('tags') or ''
                    if new_tags:
                        tag_set = set(new_tags.split(','))
                        tag_set.update(old_tags.split(','))
                        reluser.tags = ','.join(tag_set)
                    print 'With smartmerge ({}): updated existing tags {} with {}. Result: {}'.format(reluser.user.username, old_tags, new_tags, reluser.tags)
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
    help = 'Set related examiners on a period. Users are read from stdin, as a JSON encoded array of arguments to the ' \
           'RelatedExaminer model. See devilry/devilry_superadmin/examples/relatedexaminers.json for an example.'
    user_type = "examiner"

    def handle(self, *args, **options):
        from devilry.apps.core.models import RelatedExaminer
        self.get_subject_and_period(args)
        self.add_users(RelatedExaminer, args, options)
