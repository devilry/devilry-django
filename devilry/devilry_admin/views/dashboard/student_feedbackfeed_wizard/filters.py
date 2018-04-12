from django.db import models
from django.utils import timezone
from django.utils.translation import pgettext_lazy

from django_cradmin.viewhelpers import listfilter
from django_cradmin.viewhelpers.listfilter.basefilters.single import abstractselect

from devilry.devilry_cradmin import devilry_listfilter


class UserSearchExtension(devilry_listfilter.user.Search):
    def get_placeholder(self):
        return pgettext_lazy('devilry_admin studentfeedbackfeed wizard search users',
                             'Search users...')


class SearchExtension(devilry_listfilter.assignmentgroup.SearchNotAnonymous):
    def get_placeholder(self):
        return pgettext_lazy('devilry_admin studentfeedbackfeed wizard search assignments',
                             'Search assignments...')

    def get_modelfields(self):
        search_fields = super(SearchExtension, self).get_modelfields()
        search_fields.extend([
            'parentnode__long_name',
            'parentnode__short_name',
            'parentnode__parentnode__long_name',
            'parentnode__parentnode__short_name',
            'parentnode__parentnode__parentnode__long_name',
            'parentnode__parentnode__parentnode__short_name',
            'examiners__relatedexaminer__user__fullname',
            'examiners__relatedexaminer__user__shortname',
        ])
        return search_fields


class IsActiveSemester(abstractselect.AbstractBoolean):
    def get_slug(self):
        return 'semester_is_active'

    def get_label(self):
        return pgettext_lazy('group in active semester filter',
                             'Active semesters?')

    def filter(self, queryobject):
        cleaned_value = self.get_cleaned_value()
        now = timezone.now()
        if cleaned_value in ('true', 'false'):
            query = models.Q(parentnode__parentnode__start_time__lt=now,
                             parentnode__parentnode__end_time__gt=now)
            if cleaned_value == 'true':
                queryobject = queryobject.filter(query)
            elif cleaned_value == 'false':
                queryobject = queryobject.exclude(query)
        return queryobject


class OrderByDeadline(listfilter.django.single.select.AbstractOrderBy):
    def get_slug(self):
        return 'orderby_deadline'

    def get_label(self):
        return pgettext_lazy('orderby_deadline', 'Deadline ordering')

    def get_ordering_options(self):
        return [
            ('', {
                'label': pgettext_lazy('orderby_deadline', 'Deadline (ascending)'),
                'order_by': [],  # Handled with custom query in filter()
            }),
            ('deadline_descending', {
                'label': pgettext_lazy('orderby_deadline', 'Deadline (descending)'),
                'order_by': [],  # Handled with custom query in filter()
            })
        ]

    def filter(self, queryobject):
        cleaned_value = self.get_cleaned_value() or ''
        if cleaned_value == 'deadline_descending':
            return queryobject.order_by('-cached_data__last_feedbackset__deadline_datetime')
        return queryobject.order_by('cached_data__last_feedbackset__deadline_datetime')