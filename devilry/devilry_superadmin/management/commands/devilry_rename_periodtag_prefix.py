from django.core.management.base import BaseCommand

from devilry.apps.core.models import PeriodTag


class Command(BaseCommand):
    args = 'Rename period tag prefixes'

    def add_arguments(self, parser):
        parser.add_argument(
            'tag_prefix_old',
            help='The prefix to replace.'
        )
        parser.add_argument(
            'tag_prefix_new',
            help='The prefix to update period tags with.'
        )

    def handle(self, *args, **options):
        tag_prefix_old = options.get('tag_prefix_old')
        tag_prefix_new = options.get('tag_prefix_new')
        periodtag_queryset = PeriodTag.objects.filter(prefix=tag_prefix_old)

        self.stdout.write(
            'Updating prefix from \'{}\' to \'{}\' for {} period tags'.format(
                tag_prefix_old,
                tag_prefix_new,
                periodtag_queryset.count()))

        periodtag_queryset.update(prefix=tag_prefix_new)
