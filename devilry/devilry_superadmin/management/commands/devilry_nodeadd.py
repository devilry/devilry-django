from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ValidationError
from optparse import make_option


class RecordSaveModCommand(BaseCommand):
    def save_record(self, record, verbosity):
        try:
            record.full_clean()
        except ValidationError, e:
            errmsg = []
            for key, messages in e.message_dict.iteritems():
                errmsg.append('{0}: {1}'.format(key, ' '.join(messages)))
            raise CommandError('\n'.join(errmsg))
        record.save()
        if verbosity > 0:
            print '"{0}" saved successfully.'.format(record.__class__.__name__, record)


class Command(RecordSaveModCommand):
    args = '<node path> <short_name>'
    help = "Create new node. To create a root node (with no parent), use 'None' as <node path>."
    option_list = BaseCommand.option_list + (
        make_option('--admins',
            dest='admins',
            default=None,
            help='Administrator usernames separated by comma (,).'),
        make_option('--long-name',
            dest='long_name',
            default=None,
            help='Long name (Required)')
    )

    def handle(self, *args, **options):
        from devilry.apps.core.models import Node
        from devilry.coreutils.utils import get_by_path

        if len(args) != 2:
            raise CommandError('Node path and short name is required. See --help.')
        if options['long_name'] == None:
            raise CommandError('Long name is required. See --help.')
        verbosity = int(options.get('verbosity', '1'))
        node_path = args[0]
        short_name = args[1]

        if node_path == "None":
            node = None
        else:
            try:
                node = get_by_path(node_path)
            except Node.DoesNotExist, e:
                raise CommandError('Invalid node path.')

        if Node.objects.filter(short_name=short_name).count() == 0:
            long_name = options['long_name']
            record = Node(short_name=short_name, long_name=long_name, parentnode=node)
            self.save_record(record, verbosity)
        else:
            raise CommandError('Node "{0}" already exists.'.format(short_name))
