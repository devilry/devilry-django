from django.db.models.functions import Lower, Concat
from django.utils.translation import ugettext_lazy, pgettext_lazy
from django_cradmin.viewhelpers import listfilter


class OrderBy(listfilter.django.single.select.AbstractOrderBy):
    def get_slug(self):
        return 'orderby'

    def get_label(self):
        return pgettext_lazy('orderby', 'Sort')

    def get_name_ordering_options(self):
        return [
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

    def get_ordering_options(self):
        return [
            ('', {
                'label': ugettext_lazy('First deadline (newest first)'),
                'order_by': ['-first_deadline'],
            }),
            ('first_deadline_ascending', {
                'label': ugettext_lazy('First deadline (oldest first)'),
                'order_by': ['first_deadline'],
            }),
            ('publishing_time_descending', {
                'label': ugettext_lazy('Publishing time (newest first)'),
                'order_by': ['-publishing_time'],
            }),
            ('publishing_time_ascending', {
                'label': ugettext_lazy('Publishing time (oldest first)'),
                'order_by': ['publishing_time'],
            })
        ] + self.get_name_ordering_options()


class OrderByFullPath(OrderBy):
    def get_name_ordering_options(self):
        return [
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
