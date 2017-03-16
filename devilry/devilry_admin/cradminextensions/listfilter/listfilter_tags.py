from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy
from django.utils.translation import pgettext_lazy
from django_cradmin.viewhelpers import listfilter
from django_cradmin.viewhelpers.listfilter.basefilters.single import abstractselect, abstractradio


class Search(listfilter.django.single.textinput.Search):
    def get_modelfields(self):
        return [
            'prefix',
            'tag',
            'relatedstudents__user__shortname',
            'relatedstudents__user__fullname',
            'relatedexaminers__user__shortname',
            'relatedexaminers__user__fullname'
        ]

    def get_label_is_screenreader_only(self):
        return True

    def get_slug(self):
        return 'search'

    def get_label(self):
        return ugettext_lazy('Search')


class IsHiddenFilter(abstractselect.AbstractBoolean):
    def get_slug(self):
        return 'is_hidden'

    def get_label(self):
        return pgettext_lazy('period tag show hidden filter',
                             'Show hidden tags?')

    def filter(self, queryobject):
        cleaned_value = self.get_cleaned_value()
        if cleaned_value in ('true', 'false'):
            query = models.Q(models.Q(is_hidden=False) & models.Q(prefix=''))
            if cleaned_value == 'true':
                queryobject = queryobject.exclude(query)
            elif cleaned_value == 'false':
                queryobject = queryobject.filter(query)
        return queryobject


class IsHiddenRadioFilter(abstractradio.AbstractRadioFilter):
    def get_slug(self):
        return 'is_hidden'

    def get_label(self):
        return pgettext_lazy('period tag show hidden radio filter', 'Show tags')

    def get_choices(self):
        return [
            ('', 'show all tags'),
            ('show-hidden-tags-only', 'hidden tags only'),
            ('show-visible-tags-only', 'visible tags only'),
            ('show-custom-tags-only', 'custom tags only'),
            ('show-imported-tags-only', 'imported tags only'),
        ]

    def filter(self, queryobject):
        cleaned_value = self.get_cleaned_value() or ''
        if cleaned_value == '':
            queryobject = queryobject
        elif cleaned_value == 'show-hidden-tags-only':
            queryobject = queryobject.filter(is_hidden=True)
        elif cleaned_value == 'show-visible-tags-only':
            queryobject = queryobject.filter(is_hidden=False)
        elif cleaned_value == 'show-custom-tags-only':
            queryobject = queryobject.filter(prefix='')
        elif cleaned_value == 'show-imported-tags-only':
            queryobject = queryobject.exclude(prefix='')
        return queryobject
