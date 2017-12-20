from django.conf import settings
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand

from devilry.utils.management import add_output_encoding_argument


class Command(BaseCommand):
    help = 'Setup the primary domain. This domain is used for authentication redirects etc.'

    def add_arguments(self, parser):
        parser.add_argument(
            'domain',
            default=False,
            help='The domain - E.g.: "devilry.example.com".'),
        add_output_encoding_argument(parser)

    def handle(self, *args, **options):
        domain = options['domain']
        try:
            site = Site.objects.get(id=settings.SITE_ID)
        except Site.DoesNotExist:
            site = Site(id=settings.SITE_ID)
        site.domain = domain
        site.name = 'Primary domain'
        site.full_clean()
        site.save()
