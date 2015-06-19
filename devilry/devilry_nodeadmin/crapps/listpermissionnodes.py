from __future__ import unicode_literals
from django_cradmin.viewhelpers import objecttable
from django_cradmin import crapp
from devilry.apps.core.models import node


class TitleColumn(objecttable.TruncatecharsPlainTextColumn):
    modelfield = 'long_name'


class PermissionNodesListView(objecttable.ObjectTableView):
    model = node.Node
    columns = [
        TitleColumn,
    ]

    def get_queryset_for_role(self, parent_node):
        queryset = self.model.objects.filter(parentnode=parent_node)
        if not self.request.user.is_staff:
            queryset = queryset.filter(admins=self.request.user)
        return queryset


class App(crapp.App):
    appurls = [
        crapp.Url(
            r'^$',
            PermissionNodesListView.as_view(),
            name=crapp.INDEXVIEW_NAME),
    ]