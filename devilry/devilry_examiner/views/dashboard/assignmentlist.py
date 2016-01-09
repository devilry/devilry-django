from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy
from django_cradmin import crapp
from django_cradmin.viewhelpers import listbuilderview
from django_cradmin.viewhelpers import listfilter

from devilry.apps.core import models as coremodels


class AssignmentListView(listbuilderview.FilterListMixin,
                         listbuilderview.View):
    model = coremodels.Assignment

    def get_filterlist_url(self, filters_string):
        return self.request.cradmin_app.reverse_appurl(
            crapp.INDEXVIEW_NAME,
            kwargs={'filters_string': filters_string})

    def add_filterlist_items(self, filterlist):
        filterlist.append(listfilter.django.single.textinput.Search(
            slug='search',
            label=ugettext_lazy('Search'),
            label_is_screenreader_only=True,
            modelfields=['title']))

    def get_unfiltered_queryset_for_role(self, role):
        return coremodels.Assignment.objects.filter_is_examiner(user=self.request.user)


class App(crapp.App):
    appurls = [
        crapp.Url(r'^(?P<filters_string>.+)?$',
                  AssignmentListView.as_view(),
                  name=crapp.INDEXVIEW_NAME)
    ]
