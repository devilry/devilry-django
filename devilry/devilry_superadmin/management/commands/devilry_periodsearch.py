from django.db.models import Q

from devilry.apps.core.models import Period
from devilry.devilry_superadmin.management.commands.devilry_subjectsearch import NodeSearchBase


class Command(NodeSearchBase):
    help = 'Search for a period by short_name. Matches any part of the short_name.'
    nodecls = Period

    def get_qry(self, term):
        return self.nodecls.objects.filter(Q(short_name__icontains=term) | Q(parentnode__short_name__icontains=term))

    def get_short(self, record):
        return '{0}.{1}'.format(record.parentnode.short_name, record.short_name)
