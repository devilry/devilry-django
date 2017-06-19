import json
import re
from optparse import make_option

from django.conf import settings
from django.contrib.auth import get_user_model

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ValidationError

import sys

from devilry.apps.core.models import PeriodTag, RelatedStudent


class RelatedBaseCommand(BaseCommand):
    args = '<subject short name> <period short name>'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clearall',
            action='store_true',
            dest='clearall',
            default=False,
            help='Alias for for --deactivate-missing for devilry 2.x compatibility.'
        )
        parser.add_argument(
            '--deactivate-missing',
            action='store_true',
            dest='deactivate_missing',
            default=False,
            help='Set all RelatedExaminers as active=False before adding '
                 'and updating the provided users. This is useful when importing a '
                 'complete list of users, since it means that the missing '
                 'users will be deactivated.'
        )
        parser.add_argument(
            '--tag-prefix',
            dest='tag_prefix',
            default=settings.DEVILRY_SYNCSYSTEM_TAG_PREFIX,
            help='The prefix to use for imported tags. Defaults '
                 'to the value of the DEVILRY_SYNCSYSTEM_TAG_PREFIX setting '
                 '(which is {!r}).'.format(settings.DEVILRY_SYNCSYSTEM_TAG_PREFIX)
        )

    @property
    def user_type(self):
        raise NotImplementedError()

    @property
    def related_user_model_class(self):
        raise NotImplementedError()

    def get_subject_and_period(self):
        """ Get the subject and period from args """
        from devilry.apps.core.models import Subject, Period
        if len(self.args) != 2:
            raise CommandError('Subject and period is required. See --help.')
        subject_short_name = self.args[0]
        period_short_name = self.args[1]
        # Get the subject and period
        try:
            self.subject = Subject.objects.get(short_name=subject_short_name)
        except Subject.DoesNotExist, e:
            raise CommandError('Subject with short name %s does not exist.' % subject_short_name)
        try:
            self.period = Period.objects.get(short_name=period_short_name, parentnode=self.subject)
        except Period.DoesNotExist, e:
            raise CommandError('Period with short name %s does not exist.' % period_short_name)

    def _deactivate_all(self):
        if self.related_user_model_class == RelatedStudent:
            queryset = self.period.relatedstudent_set
        else:
            queryset = self.period.relatedexaminer_set
        queryset.update(active=False)

    def add_users(self):
        """ Add the users read from stdin to the given relatedmanager """
        if self.deactivate_missing:
            self._deactivate_all()
        user_model = get_user_model()
        for kw in self.input_data:
            username = kw.pop('username', None)
            email = kw.pop('email', None)
            tags_string = kw.pop('tags', '').strip()
            kw.setdefault('active', True)
            user, created = user_model.objects.get_or_create_user(
                username=username, email=email)
            if not self._update_related_user(user, kw, tags_string):
                self._create_reluser(user, kw, tags_string)
        if self.verbosity > 0:
            print "Added/updated {count} related {user_type}s to {subject}.{period}".format(
                count=len(self.input_data), user_type=self.user_type,
                subject=self.subject.short_name, period=self.period.short_name)

    def _split_tags_string(self, tags_string):
        return re.split(r'\s*,\s*', tags_string)

    def _clear_tags_for_relateduser(self, relateduser):
        kwargs = {
            'periodtag__prefix': self.tag_prefix,
            'periodtag__period': self.period
        }
        if self.related_user_model_class == RelatedStudent:
            kwargs['relatedstudent'] = relateduser
            PeriodTag.relatedstudents.through.objects.filter(**kwargs).delete()
        else:
            kwargs['relatedexaminer'] = relateduser
            PeriodTag.relatedexaminers.through.objects.filter(**kwargs).delete()

    def _add_relateduser_to_tag(self, tag, relateduser):
        if self.related_user_model_class == RelatedStudent:
            tag.relatedstudents.add(relateduser)
        else:
            tag.relatedexaminers.add(relateduser)

    def _update_tags(self, relateduser, tags_string):
        self._clear_tags_for_relateduser(relateduser=relateduser)
        if not tags_string:
            return
        tags_string_list = self._split_tags_string(tags_string)
        for tagname in tags_string_list:
            tag, created = PeriodTag.objects.get_or_create(
                prefix=self.tag_prefix,
                tag=tagname,
                period=self.period)
            self._add_relateduser_to_tag(tag=tag, relateduser=relateduser)

    def _update_related_user(self, user, kw, tags_string):
        try:
            relateduser = self.related_user_model_class.objects.get(
                period=self.period, user=user)
        except self.related_user_model_class.DoesNotExist:
            return False
        else:
            for key, value in kw.iteritems():
                setattr(relateduser, key, value)
            self._save_related_user(relateduser, 'Updated')
            self._update_tags(relateduser, tags_string)
            return True

    def _create_reluser(self, user, kw, tags_string):
        relateduser = self.related_user_model_class(
            period=self.period, user=user, **kw)
        self._save_related_user(relateduser, 'Added')
        self._update_tags(relateduser, tags_string)

    def _save_related_user(self, relateduser, mode):
        try:
            relateduser.full_clean()
        except ValidationError:
            raise CommandError('Invalid related user: "{0}"'.format(relateduser))
        else:
            relateduser.save()
            if self.verbosity > 1:
                print "{0} {1} {2}".format(mode, self.user_type, relateduser)

    def handle(self, *args, **options):
        self.args = args
        self.options = options
        self.verbosity = int(options.get('verbosity', '1'))
        self.tag_prefix = options.get('tag_prefix')
        self.deactivate_missing = options.get('deactivate_missing') or options.get('clearall')
        jsondata = sys.stdin.read()
        self.input_data = json.loads(jsondata)


class Command(RelatedBaseCommand):
    help = 'Set related examiners on a period. Users are read from stdin, ' \
           'as a JSON encoded array of arguments to the RelatedExaminer model. ' \
           'See devilry/apps/superadmin/examples/relatedexaminers.json for an example.'

    @property
    def user_type(self):
        return "examiner"

    @property
    def related_user_model_class(self):
        from devilry.apps.core.models import RelatedExaminer
        return RelatedExaminer

    def handle(self, *args, **options):
        super(Command, self).handle(*args, **options)
        self.get_subject_and_period()
        self.add_users()
