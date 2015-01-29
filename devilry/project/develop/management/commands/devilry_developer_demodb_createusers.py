from django.core.management.base import BaseCommand

from devilry.utils.demodb import demousers


class Command(BaseCommand):
    help = 'Add the demodb users.'

    def handle(self, *args, **options):
        demousers.Users().create_all_users()
