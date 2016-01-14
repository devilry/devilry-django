from django.conf import settings
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
        return super(AbstractSearch, self).filter(queryobject=queryobject)


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
        if settings.DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND:
            shortname_ascending_label = ugettext_lazy('Email')
            shortname_descending_label = ugettext_lazy('Email (descending)')
        else:
            shortname_ascending_label = ugettext_lazy('Username')
            shortname_descending_label = ugettext_lazy('Username (descending)')
        return [
            ('', {
                'label': ugettext_lazy('Name'),
                'order_by': [],  # Handled with custom query in filter()
            }),
            ('name_descending', {
                'label': ugettext_lazy('Name (descending)'),
                'order_by': [],  # Handled with custom query in filter()
            }),
            ('shortname_ascending', {
                'label': shortname_ascending_label,
                'order_by': [],  # Handled with custom query in filter()
            }),
            ('shortname_descending', {
                'label': shortname_descending_label,
                'order_by': [],  # Handled with custom query in filter()
            }),
            ('lastname_ascending', {
                'label': ugettext_lazy('Last name'),
                'order_by': [],  # Handled with custom query in filter()
            }),
            ('lastname_descending', {
                'label': ugettext_lazy('Last name (descending)'),
                'order_by': [],  # Handled with custom query in filter()
            }),
        ]

    def filter(self, queryobject):
        cleaned_value = self.get_cleaned_value() or ''
        if cleaned_value == '':
            return queryobject.extra_order_by_fullname_of_first_candidate()
        elif cleaned_value == 'name_descending':
            return queryobject.extra_order_by_fullname_of_first_candidate(descending=True)
        elif cleaned_value == 'shortname_ascending':
            return queryobject.extra_order_by_shortname_of_first_candidate()
        elif cleaned_value == 'shortname_descending':
            return queryobject.extra_order_by_shortname_of_first_candidate(descending=True)
        elif cleaned_value == 'lastname_ascending':
            return queryobject.extra_order_by_lastname_of_first_candidate()
        elif cleaned_value == 'lastname_descending':
            return queryobject.extra_order_by_lastname_of_first_candidate(descending=True)
        else:
            return super(OrderByNotAnonymous, self).filter(queryobject=queryobject)


class OrderByAnonymous(AbstractOrderBy):
    def get_ordering_options(self):
        return [
            ('', {
                'label': ugettext_lazy('Anonymous ID'),
                'order_by': [],  # Handled with custom query in filter()
            }),
            ('name_descending', {
                'label': ugettext_lazy('Anonymous ID (descending)'),
                'order_by': [],  # Handled with custom query in filter()
            }),
        ]

    def filter(self, queryobject):
        cleaned_value = self.get_cleaned_value() or ''
        if cleaned_value == '':
            return queryobject.extra_order_by_relatedstudents_anonymous_id_of_first_candidate()
        elif cleaned_value == 'name_descending':
            return queryobject.extra_order_by_relatedstudents_anonymous_id_of_first_candidate(descending=True)
        else:
            return super(OrderByAnonymous, self).filter(queryobject=queryobject)


class OrderByAnonymousUsesCustomCandidateIds(AbstractOrderBy):
    def get_ordering_options(self):
        return [
            ('', {
                'label': ugettext_lazy('Candidate ID'),
                'order_by': [],  # Handled with custom query in filter()
            }),
            ('name_descending', {
                'label': ugettext_lazy('Candidate ID (descending)'),
                'order_by': [],  # Handled with custom query in filter()
            }),
        ]

    def filter(self, queryobject):
        cleaned_value = self.get_cleaned_value() or ''
        if cleaned_value == '':
            return queryobject.extra_order_by_candidates_candidate_id_of_first_candidate()
        elif cleaned_value == 'name_descending':
            return queryobject.extra_order_by_candidates_candidate_id_of_first_candidate(descending=True)
        else:
            return super(OrderByAnonymousUsesCustomCandidateIds, self).filter(queryobject=queryobject)
