from django.utils.translation import gettext_lazy
from cradmin_legacy.viewhelpers import listfilter
from django.utils.encoding import smart_str


class Search(listfilter.django.single.textinput.Search):
    def __init__(self, label_is_screenreader_only=True):
        super(Search, self).__init__(
            slug='search',
            label=gettext_lazy('Search'),
            label_is_screenreader_only=label_is_screenreader_only
        )

    def get_placeholder(self):
        return gettext_lazy('Search listed objects ...')

    def get_modelfields(self):
        return [
            'fullname',
            'shortname',
            'username__username',
            'useremail__email',
        ]

    def get_cleaned_value(self):
        out = super().get_cleaned_value()
        return smart_str(out, strings_only=True)
