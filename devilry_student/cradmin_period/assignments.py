from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django_cradmin.viewhelpers import objecttable
from django_cradmin import crapp

from devilry.apps.core.models import AssignmentGroup


class LongNameColumn(objecttable.SingleActionColumn):
    modelfield = 'id'

    def render_value(self, group):
        return group.parentnode.long_name

    def get_actionurl(self, group):
        return reverse('devilry_student_group-add_delivery-INDEX', kwargs={
            'roleid': group.id
        })


class AssignmentGroupListView(objecttable.ObjectTableView):
    model = AssignmentGroup
    columns = [
        LongNameColumn,
    ]
    searchfields = ['parentnode__long_name', 'parentnode__short_name']

    def get_queryset_for_role(self, period):
        return AssignmentGroup.objects\
            .filter(parentnode__parentnode=period)\
            .filter_student_has_access(user=self.request.user)\
            .select_related('parentnode', 'parentnode__parentnode', 'parentnode__parentnode__parentnode')


class App(crapp.App):
    appurls = [
        crapp.Url(
            r'^$',
            AssignmentGroupListView.as_view(),
            name=crapp.INDEXVIEW_NAME),
    ]
