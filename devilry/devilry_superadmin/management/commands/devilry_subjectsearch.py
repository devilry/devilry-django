from django.core.management.base import BaseCommand

from devilry.apps.core.models import Subject
from devilry.utils.management import add_output_encoding_argument


class NodeSearchBase(BaseCommand):
    nodecls = None
    args = '[search|empty for all]'
    attrs = ['short_name', 'long_name']

    def add_arguments(self, parser):
        parser.add_argument(
            '--short_name-only',
            action='store_true',
            dest='short_name_only',
            default=False,
            help='Only print short name (one line per short_name)'),
        add_output_encoding_argument(parser)

    def _print_details(self, record):
        print(self.get_short(record))
        print('   id: {}'.format(record.id))
        for attrname in self.attrs:
            attr = getattr(record, attrname)
            try:
                attr = attr.encode(self.outputencoding)
            except:
                attr = attr.encode('ascii', 'replace')
            print('   {attrname}: {attr}'.format(attrname=attrname,
                                                 attr=attr))
        # print '   admins:'
        # for admin in record.admins.all():
        #     print '        - {0}'.format(admin)

    def show_search_results(self, options, qry):
        for record in qry:
            if options['short_name_only']:
                print(self.get_short(record))
            else:
                self._print_details(record)

    def handle(self, *args, **options):
        self.outputencoding = options['outputencoding']
        if len(args) == 1:
            qry = self.get_qry(args[0])
        else:
            qry = self.nodecls.objects.all()
        self.show_search_results(options, qry)

    def get_qry(self, term):
        return self.nodecls.objects.filter(short_name__icontains=term)

    def get_short(self, record):
        return record.short_name


class Command(NodeSearchBase):
    help = 'Search for a subject by short_name. Matches any part of the short_name.'
    nodecls = Subject
