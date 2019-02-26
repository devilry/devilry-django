from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction


class RecordSaveModCommand(BaseCommand):
    def save_record(self, record):
        try:
            record.full_clean()
        except ValidationError as e:
            errmsg = []
            for key, messages in e.message_dict.items():
                errmsg.append('{0}: {1}'.format(key, ' '.join(messages)))
            raise CommandError('\n'.join(errmsg))
        record.save()
        return record


class Command(RecordSaveModCommand):
    help = 'Create new subject.'

    def add_arguments(self, parser):
        parser.add_argument(
            'short_name',
            default='',
            help='Short name for the subject. (Required)'),
        parser.add_argument(
            '--long-name',
            dest='long_name',
            default=None,
            required=True,
            help='Long name (Required)')
        parser.add_argument(
            '--permission-groups',
            dest='permission_groups',
            required=False,
            default=[],
            nargs='*',
            help='The name of the permission groups separated by blank spaces. '
                 'Must be subject or department groups. (Not required)'
        )

    def handle(self, *args, **options):
        from devilry.apps.core.models import Subject
        verbosity = int(options.get('verbosity', '1'))
        short_name = options['short_name']
        long_name = options['long_name']
        permission_groups = options.get('permission_groups')

        if Subject.objects.filter(short_name=short_name).exists():
            raise CommandError('Subject "{0}" already exists.'.format(short_name))
        else:
            with transaction.atomic():
                subject = Subject(short_name=short_name, long_name=long_name)
                record = self.save_record(subject)

                if len(permission_groups) > 0:
                    for permission_group in permission_groups:
                        call_command('devilry_permissiongroup_add_subject', short_name, permission_group)

                if verbosity > 0:
                    print('{} "{}" saved successfully.'.format(
                        record.__class__.__name__, str(record).encode('utf-8')))
