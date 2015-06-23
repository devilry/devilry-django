from __future__ import unicode_literals
from django.core import exceptions
from django.core.urlresolvers import reverse

from django_cradmin.viewhelpers import objecttable
from django_cradmin import crapp
from django_cradmin import crinstance

from devilry.apps.core.models import node


# class TitleColumn(objecttable.TruncatecharsPlainTextColumn):
#     modelfield = 'short_name'

class TitleColumn(objecttable.SingleActionColumn):
    modelfield = 'long_name'

    def get_actionurl(self, node):
        return '/devilry_nodeadmin/{}/listnodes_index/'.format(node.id)

    # def get_actionurl(self, node):
    #     return crinstance.reverse_cradmin_url(
    #         instanceid='nodepermission_listing',
    #         appname='devilry_nodeadmin',
    #         roleid=node.id-1
    #     )



class PermissionNodesListView(objecttable.ObjectTableView):
    model = node.Node
    columns = [
        TitleColumn,
    ]

    def get_queryset_for_role(self, role):
        queryset = node.Node.objects.filter(parentnode=role)
        if self.request.user.is_superuser:
            return queryset

        parent = role
        while not self.request.user in parent.admins.all():
            if parent.parentnode == None:
                raise exceptions.PermissionDenied("User does not have access to this role")
            parent = parent.parentnode

        return queryset

class App(crapp.App):
    appurls = [
        crapp.Url(
            r'^$',
            PermissionNodesListView.as_view(),
            name=crapp.INDEXVIEW_NAME),
    ]