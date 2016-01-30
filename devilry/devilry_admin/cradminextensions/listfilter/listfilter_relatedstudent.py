from django.conf import settings
from django.db.models.functions import Lower, Concat
from django.utils.translation import ugettext_lazy
from django_cradmin.viewhelpers import listfilter


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
