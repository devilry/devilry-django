

from django.db import models
from django.utils.translation import gettext_lazy, pgettext_lazy
from cradmin_legacy.viewhelpers import listfilter
from cradmin_legacy.viewhelpers.listfilter.basefilters.single import abstractselect, abstractradio

from devilry.apps.core.models import PeriodTag


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
        return gettext_lazy('Search')

    def get_placeholder(self):
        return gettext_lazy('Search listed objects ...')


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
            ('', gettext_lazy('show all tags')),
            ('show-hidden-tags-only', gettext_lazy('hidden tags only')),
            ('show-visible-tags-only', gettext_lazy('visible tags only')),
            ('show-custom-tags-only', gettext_lazy('custom tags only')),
            ('show-imported-tags-only', gettext_lazy('imported tags only')),
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


class AbstractTagSelectFilter(abstractselect.AbstractSelectFilter):
    """
    Abstract class for supporting tag selection.

    Override the :method:`.AbstractTagSelectFilter.filter` method to
    handle filtering for period tags.
    """
    def __init__(self, **kwargs):
        self.period = kwargs.pop('period', None)
        super(AbstractTagSelectFilter, self).__init__(**kwargs)

    def get_notag_value(self):
        return 'notag'

    def get_slug(self):
        return 'tag'

    def copy(self):
        copy = super(AbstractTagSelectFilter, self).copy()
        copy.period = self.period
        return copy

    def get_label(self):
        return pgettext_lazy('tag', 'Has tag')

    def __get_choices(self):
        choices = [
            ('', pgettext_lazy('tag', 'Any')),
            (self.get_notag_value(), pgettext_lazy('tag', 'NO TAG'))
        ]
        choices.extend(PeriodTag.objects.tags_and_ids_tuple_list(period=self.period))
        return choices

    def get_choices(self):
        if not hasattr(self, '_choices'):
            self._choices = self.__get_choices()
        return self._choices

    def filter(self, queryobject):
        """
        Override this to filter period tags.

        Args:
            queryobject: A ``QuerySet``.

        Returns:
            (QuerySet): Returns a ``QuerySet``.
        """
        raise NotImplementedError()
