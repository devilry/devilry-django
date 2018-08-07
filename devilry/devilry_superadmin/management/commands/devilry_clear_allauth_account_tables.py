from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialToken, SocialAccount
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Clear the allauth user info tables.'

    def handle(self, *args, **options):
        SocialToken.objects.all().delete()
        EmailAddress.objects.all().delete()
        SocialAccount.objects.all().delete()
