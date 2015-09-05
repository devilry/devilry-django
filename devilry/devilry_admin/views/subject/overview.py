from __future__ import unicode_literals
from django.views.generic import TemplateView

from django_cradmin import crapp
from django_cradmin.viewhelpers.objecttable import ObjectTableView
from devilry.apps.core.models import Period


class Overview(ObjectTableView):
    template_name = 'devilry_admin/subject/overview.django.html'
    model = Period

    def get_queryset_for_role(self, role):
        """
        Get a queryset with all objects of :obj:`.model`  that
        the current role can access.
        """
        return self.get_model_class().objects.filter(parentnode=role)

class App(crapp.App):
    appurls = [
        crapp.Url(r'^$', Overview.as_view(), name=crapp.INDEXVIEW_NAME)
    ]
