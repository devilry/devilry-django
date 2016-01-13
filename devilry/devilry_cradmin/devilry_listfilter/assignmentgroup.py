from django.db.models.functions import Lower, Concat
from django.utils.translation import ugettext_lazy
from django_cradmin.viewhelpers import listfilter


class AbstractSearch(listfilter.django.single.textinput.Search):
    def __init__(self, label_is_screenreader_only=True):
        super(AbstractSearch, self).__init__(
            slug='search',
            label=ugettext_lazy('Search'),
            label_is_screenreader_only=label_is_screenreader_only
        )

    def filter(self, queryobject):
        return super(AbstractSearch, self).filter(queryobject=queryobject).distinct()


class SearchNotAnonymous(AbstractSearch):
    def get_modelfields(self):
        return [
            'candidates__relatedstudent__user__fullname',
            'candidates__relatedstudent__user__shortname',
        ]


class SearchAnonymous(AbstractSearch):
    def get_modelfields(self):
        return [
            'candidates__relatedstudent__candidate_id',
            'candidates__relatedstudent__automatic_anonymous_id',
        ]


class SearchAnonymousUsesCustomCandidateIds(AbstractSearch):
    def get_modelfields(self):
        return [
            'candidates__candidate_id',
        ]


class AbstractOrderBy(listfilter.django.single.select.AbstractOrderBy):
    def __init__(self, label_is_screenreader_only=False):
        super(AbstractOrderBy, self).__init__(
            slug='orderby',
            label=ugettext_lazy('Order by'),
            label_is_screenreader_only=label_is_screenreader_only
        )

    def filter(self, queryobject):
        return super(AbstractOrderBy, self).filter(queryobject=queryobject).distinct()


class OrderByNotAnonymous(AbstractOrderBy):
    def get_ordering_options(self):
        return [
            ('', {
                'label': ugettext_lazy('Name'),
                'order_by': [Lower(Concat('candidates__relatedstudent__user__fullname',
                                          'candidates__relatedstudent__user__shortname'))],
            }),
            ('name_descending', {
                'label': ugettext_lazy('Name (reverse order)'),
                'order_by': [Lower(Concat('candidates__relatedstudent__user__fullname',
                                          'candidates__relatedstudent__user__shortname')).desc()],
            }),
            # ('publishing_time_descending', {
            #     'label': ugettext_lazy('Publishing time (oldest first)'),
            #     'order_by': ['publishing_time'],
            # }),
            # ('name_ascending', {
            #     'label': ugettext_lazy('Name'),
            #     'order_by': [Lower(Concat('parentnode__parentnode__short_name',
            #                               'parentnode__short_name',
            #                               'long_name'))],
            # }),
            # ('name_descending', {
            #     'label': ugettext_lazy('Name (reverse order)'),
            #     'order_by': [Lower(Concat('parentnode__parentnode__short_name',
            #                               'parentnode__short_name',
            #                               'long_name')).desc()],
            # }),
        ]
