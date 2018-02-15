from django.conf import settings
from django.db.models.functions import Lower, Concat
from django.utils.translation import ugettext_lazy, pgettext_lazy
from django_cradmin.viewhelpers import listfilter
from django_cradmin.viewhelpers.listfilter.basefilters.single import abstractselect

from devilry.devilry_admin.cradminextensions.listfilter import listfilter_tags


class OrderRelatedStudentsFilter(listfilter.django.single.select.AbstractOrderBy):
    def get_ordering_options(self):
        if settings.DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND:
            shortname_ascending_label = ugettext_lazy('Email')
            shortname_descending_label = ugettext_lazy('Email descending')
        else:
            shortname_ascending_label = ugettext_lazy('Username')
            shortname_descending_label = ugettext_lazy('Username descending')

        # NOTE: We use Concat below to get sorting that works even when the user
        #       does not have a fullname, and we use Lower to sort ignoring case.
        return [
            ('', {
                'label': ugettext_lazy('Name'),
                'order_by': [Lower(Concat('user__fullname', 'user__shortname'))],
            }),
            ('name_descending', {
                'label': ugettext_lazy('Name descending'),
                'order_by': [Lower(Concat('user__fullname', 'user__shortname')).desc()],
            }),
            ('lastname_ascending', {
                'label': ugettext_lazy('Last name'),
                'order_by': [Lower('user__lastname')],
            }),
            ('lastname_descending', {
                'label': ugettext_lazy('Last name descending'),
                'order_by': [Lower('user__lastname').desc()],
            }),
            ('shortname_ascending', {
                'label': shortname_ascending_label,
                'order_by': ['user__shortname'],
            }),
            ('shortname_descending', {
                'label': shortname_descending_label,
                'order_by': ['-user__shortname'],
            }),
        ]

    def get_slug(self):
        return 'orderby'

    def get_label(self):
        return pgettext_lazy('orderby', 'Sort')


class IsActiveFilter(listfilter.django.single.select.Boolean):
    def get_slug(self):
        return 'active'

    def get_label(self):
        return pgettext_lazy('listfilter relateduser', 'Is active?')


class Search(listfilter.django.single.textinput.Search):
    def get_modelfields(self):
        return [
            'user__fullname',
            'user__shortname',
            'periodtag__tag',
        ]

    def get_label_is_screenreader_only(self):
        return True

    def get_slug(self):
        return 'search'

    def get_label(self):
        return ugettext_lazy('Search')

    def get_placeholder(self):
        return ugettext_lazy('Search listed objects ...')


class TagSelectFilter(listfilter_tags.AbstractTagSelectFilter):
    def filter(self, queryobject):
        cleaned_value = self.get_cleaned_value() or ''
        if cleaned_value != '':
            queryobject = queryobject.filter(periodtag__id=cleaned_value)
        return queryobject
