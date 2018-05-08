from getpass import getpass

from allauth.socialaccount.models import SocialApp
from devilry.devilry_dataporten_allauth.provider import DevilryDataportenProvider
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Setup Dataporten provider for Django allauth.'

    def add_arguments(self, parser):
        parser.add_argument(
            'client_id',
            help='The Dataporten OAuth Client ID.'),

    def handle(self, *args, **options):
        try:
            site = Site.objects.get(id=settings.SITE_ID)
        except Site.DoesNotExist:
            self.stderr.write('No primary domain configured. Please run: '
                              'python manage.py devilry_setup_primary_domain')
            raise SystemExit()

        client_id = options['client_id']
        secret = getpass('Please type your Dataporten OAuth Client Secret: ')
        if not secret:
            self.stderr.write('Secret is required')
            raise SystemExit()
        try:
            socialapp = SocialApp.objects.get(provider=DevilryDataportenProvider.id)
        except SocialApp.DoesNotExist:
            socialapp = SocialApp(provider=DevilryDataportenProvider.id)
        socialapp.name = 'Devilry Dataporten'
        socialapp.client_id = client_id
        socialapp.secret = secret
        socialapp.full_clean()
        socialapp.save()

        if not socialapp.sites.filter(id=settings.SITE_ID).exists():
            socialapp.sites.add(site)

        self.stdout.write('Dataporten provider successfully configured.')
