from django.db.models import Count

from djangorestframework.views import InstanceModelView
from djangorestframework.resources import ModelResource
from djangorestframework.permissions import IsAuthenticated
from devilry.apps.core.models import Node, Assignment
from devilry.devilry_subjectadmin.rest.auth import BaseIsAdmin, nodeadmin_required


class IsNodeAdmin(BaseIsAdmin):
    ID_KWARG = 'id'

    def check_permission( self, user ):
        nodeid = self.get_id()
        nodeadmin_required( user, nodeid )



class NodeDetailsResource(ModelResource):
    model = Node
    fields = ('id', 'short_name', 'long_name', 'etag',
            'subject_count', 'assignment_count', 'period_count', 'subjects',
            'breadcrumbs', 'path', 'childnodes')

    def _serialize_subject(self, subject):
        return {
            'id': subject.id,
            'short_name': subject.short_name,
            'long_name': subject.long_name
        }

    def subjects( self, instance ):
        return map(self._serialize_subject, instance.subjects.all())

    # stats
    def subject_count( self, instance ):
        # [?] does it make recursive calls to the top of the hierarchy? accumulates the sum of all subjects?
        return instance.subjects.count()

    def assignment_count( self, instance ):
        return Assignment.objects.filter(parentnode__parentnode__parentnode=instance).count()

    def period_count( self, instance ):
        # [?] downward-recursive?
        result = instance.subjects.all().aggregate( Count('periods') )
        return result['periods__count']


    def _is_admin_or_superuser(self, node):
        return self.view.request.user.is_superuser or node.is_admin(self.view.request.user)

    def path( self, instance ):
        path = []
        node = instance
        while True:
            toplevel = node.parentnode == None or not self._is_admin_or_superuser(node.parentnode)
            if toplevel:
                path.append({
                    'id': node.id,
                    'short_name': node.get_path()
                })
                break
            else:
                path.append({
                    'id': node.id,
                    'short_name': node.short_name
                })
            node = node.parentnode
        path.reverse()
        return path


    def _serialize_node(self, node):
        return {
            'id': node.id,
            'short_name': node.short_name,
            'long_name': node.long_name
        }

    def childnodes(self, instance):
        return [self._serialize_node(node) for node in instance.child_nodes.all()]




class NodeDetails( InstanceModelView ):
    resource = NodeDetailsResource
    permissions = (IsAuthenticated, IsNodeAdmin,)
    allowed_methods = ('get',)

    def get_instance_data(self, instance):
        return instance
