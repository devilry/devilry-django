from django.conf import settings
from django.utils.translation import ugettext_lazy, pgettext_lazy
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
            label=pgettext_lazy('orderby', 'Sort'),
            label_is_screenreader_only=label_is_screenreader_only
        )

    def get_extra_ordering_options_pre(self):
        return []

    def get_common_ordering_options(self):
        return [
            ('points_descending', {
                'label': pgettext_lazy('orderby', 'Points (highest first)'),
                'order_by': ['-grading_points'],
            }),
            ('points_ascending', {
                'label': pgettext_lazy('orderby', 'Points (lowest first)'),
                'order_by': ['grading_points'],
            }),
            ('last_commented_by_student_descending', {
                'label': pgettext_lazy('orderby', 'Recently commented by student'),
                'order_by': [],  # Handled with custom query in filter()
            }),
            ('last_commented_by_student_ascending', {
                'label': pgettext_lazy('orderby', 'Least recently commented by student'),
                'order_by': [],  # Handled with custom query in filter()
            }),
        ]

    def get_ordering_options(self):
        ordering_options = self.get_extra_ordering_options_pre()
        ordering_options.extend(self.get_common_ordering_options())
        return ordering_options

    def filter(self, queryobject):
        cleaned_value = self.get_cleaned_value() or ''
        if cleaned_value == 'last_commented_by_student_ascending':
            return queryobject.extra_order_by_datetime_of_last_student_comment()
        elif cleaned_value == 'last_commented_by_student_descending':
            return queryobject.extra_order_by_datetime_of_last_student_comment(descending=True)
        return super(AbstractOrderBy, self).filter(queryobject=queryobject).distinct()


class OrderByNotAnonymous(AbstractOrderBy):
    def get_extra_ordering_options_pre(self):
        if settings.DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND:
            shortname_ascending_label = pgettext_lazy('orderby', 'Email')
            shortname_descending_label = pgettext_lazy('orderby', 'Email (descending)')
        else:
            shortname_ascending_label = pgettext_lazy('orderby', 'Username')
            shortname_descending_label = pgettext_lazy('orderby', 'Username (descending)')
        return [
            ('', {
                'label': pgettext_lazy('orderby', 'Name'),
                'order_by': [],  # Handled with custom query in filter()
            }),
            ('name_descending', {
                'label': pgettext_lazy('orderby', 'Name (descending)'),
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
                'label': pgettext_lazy('orderby', 'Last name'),
                'order_by': [],  # Handled with custom query in filter()
            }),
            ('lastname_descending', {
                'label': pgettext_lazy('orderby', 'Last name (descending)'),
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
    def get_extra_ordering_options_pre(self):
        return [
            ('', {
                'label': pgettext_lazy('orderby', 'Anonymous ID'),
                'order_by': [],  # Handled with custom query in filter()
            }),
            ('name_descending', {
                'label': pgettext_lazy('orderby', 'Anonymous ID (descending)'),
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
    def get_extra_ordering_options_pre(self):
        return [
            ('', {
                'label': pgettext_lazy('orderby', 'Candidate ID'),
                'order_by': [],  # Handled with custom query in filter()
            }),
            ('name_descending', {
                'label': pgettext_lazy('orderby', 'Candidate ID (descending)'),
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
