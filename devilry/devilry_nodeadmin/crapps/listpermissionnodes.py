from __future__ import unicode_literals
from django.core import exceptions
from django_cradmin.viewhelpers import objecttable
from django_cradmin import crapp
from devilry.apps.core.models import node


class TitleColumn(objecttable.TruncatecharsPlainTextColumn):
    modelfield = 'long_name'

# class TitleColumn(objecttable.SingleActionColumn):
#     modelfield = 'long_name'
#
#     def get_actionurl(self, node):
#         return crinstance.reverse_cradmin_url(
#             instanceid='devilry_nodeadmin',
#             appname='listnodes_index',
#             roleid=node.id
#         )



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

    # def get_queryset_for_role(self, role):
    #     if not self.request.user in role.admins.all() and not self.request.user.is_superuser:
    #         raise exceptions.PermissionDenied('User does not have access to parentnode')
    #
    #     return node.Node.objects.filter(parentnode=role)

    # def get_queryset_for_role(self, parent_node):
    #     queryset = self.model.objects.filter(parentnode=parent_node)
    #     if not self.request.user.is_superuser:
    #         queryset = queryset.filter(admins=self.request.user)
    #     return queryset


class App(crapp.App):
    appurls = [
        crapp.Url(
            r'^$',
            PermissionNodesListView.as_view(),
            name=crapp.INDEXVIEW_NAME),
    ]