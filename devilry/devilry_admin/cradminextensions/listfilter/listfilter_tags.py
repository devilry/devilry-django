from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy
from django_cradmin.viewhelpers import listfilter


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
