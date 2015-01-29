from django.core.management.base import BaseCommand, CommandError
from devilry.project.develop.testhelpers.corebuilder import NodeBuilder


class Command(BaseCommand):
    help = 'Add a node to the database.'
    args = '<nodename>'

    def handle(self, *args, **options):
        if len(args) < 1:
            raise CommandError('See --help')
        nodename = args[0]
        NodeBuilder(nodename)
