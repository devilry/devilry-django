from django.db.models.functions import Lower, Concat
from django.utils.translation import ugettext_lazy
from django_cradmin.viewhelpers import listfilter


class OrderByFullPath(listfilter.django.single.select.AbstractOrderBy):
    def get_ordering_options(self):
        return [
            ('', {
                'label': ugettext_lazy('Publishing time (newest first)'),
                'order_by': ['-publishing_time'],
            }),
            ('publishing_time_descending', {
                'label': ugettext_lazy('Publishing time (oldest first)'),
                'order_by': ['publishing_time'],
            }),
            ('name_ascending', {
                'label': ugettext_lazy('Name'),
                'order_by': [Lower(Concat('parentnode__parentnode__short_name',
                                          'parentnode__short_name',
                                          'long_name'))],
            }),
            ('name_descending', {
                'label': ugettext_lazy('Name (descending)'),
                'order_by': [Lower(Concat('parentnode__parentnode__short_name',
                                          'parentnode__short_name',
                                          'long_name')).desc()],
            }),
        ]
