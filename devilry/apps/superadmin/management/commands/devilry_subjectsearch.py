from django.core.management.base import BaseCommand, CommandError
from optparse import make_option

from devilry.apps.core.models import Subject


class Command(BaseCommand):
    args = '[search|empty for all]'
    help = 'Search for a subject by short_name. Matches any part of the short_name.'
    option_list = BaseCommand.option_list + (
        make_option('--short_name-only',
            action='store_true',
            dest='short_name_only',
            default=False,
            help='Only print short name (one line per short_name)'),
    )

    def handle(self, *args, **options):
        if len(args) == 1:
            qry = Subject.objects.filter(short_name__icontains=args[0])
        else:
            qry = Subject.objects.all()

        for subject in qry:
            if options['short_name_only']:
                print subject.short_name
            else:
                self._print_subject_details(subject)

    def _print_subject_details(self, subject):
        print '{0}:'.format(subject.short_name)
        for attrname in ('short_name', 'long_name'):
            print '   {attrname}: {attr}'.format(attrname=attrname,
                                                 attr=getattr(subject, attrname))
        print '   admins:'
        for admin in subject.admins.all():
            print '        - {0}'.format(admin)
