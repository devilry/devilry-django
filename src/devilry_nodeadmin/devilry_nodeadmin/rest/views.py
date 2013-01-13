# -*- coding: utf-8 -*-

# [/] should be split into files, once completed
# [/] should make use of base class definitions from devilry legacy

from django.http import HttpResponse

from devilry.apps.core.models import Node, Subject, DevilryUserProfile, Period, RelatedStudent

from djangorestframework.views import ModelView, ListModelView, InstanceModelView
from djangorestframework.mixins import InstanceMixin, ReadModelMixin
from djangorestframework.resources import ModelResource
from djangorestframework.permissions import IsAuthenticated

from devilry_subjectadmin.rest.auth import BaseIsAdmin, nodeadmin_required

from django.db.models import Count, Min, Max




class NodeResource( ModelResource ):
    model = Node
    fields = (  'id', 'short_name', 'long_name',
                'etag', 'predecessor', 'children', 'most_recent_start_time', )
    allowed_methods = ('get' ,)

    # [->] to RelatedNodeDetails

    def most_recent_start_time( self, instance ):
        # [/] strftime
        # [!] needs a good way of collecting the most recent period
        # that on a later stage can be developed into an ordering operator
        result = Period.objects.filter( parentnode__parentnode=instance ).\
        aggregate( Max( 'start_time' )  )
        return result['start_time__max']

    # Hierarchy data

    def predecessor( self, instance ):
        parent_serializer = ParentNodeResource()
        return parent_serializer.serialize( instance.parentnode )

    def children( self, instance ):
        child_serializer = ChildNodeResource()
        candidates = Node.objects.filter( parentnode=instance )
        return child_serializer.serialize_iter( candidates )



class ChildNodeResource( NodeResource ):
    model = Node
    fields = (  'id', 'short_name', 'long_name', 'predecessor', 'most_recent_start_time', )


class ParentNodeResource( NodeResource ):
    model = Node
    fields = (  'id', 'short_name', 'long_name',  )



class RelatedNodes( ListModelView ):
    """
    All nodes where the user is either admin or superadmin
    """
    
    resource = NodeResource
    permissions = (IsAuthenticated, ) # [+] restrict to Admin

    def get_queryset( self ):
        nodes = Node.where_is_admin_or_superadmin( self.request.user )
        nodes = nodes.exclude( parentnode__in=nodes )
        return nodes


class RelatedNodeChildren( ListModelView ):
    resource = ChildNodeResource
    permissions = (IsAuthenticated, ) # [+] restrict to Admin
    allowed_methods = ('get' ,)

    def get_queryset( self ):
        nodes = Node.where_is_admin_or_superadmin( self.request.user ).filter(
            parentnode__pk=self.kwargs['parentnode__pk']
        )
        return nodes



class NodeSubjectResource( ModelResource ):
    model = Subject
    fields = ( 'id', 'short_name', 'long_name', )

class NodeDetailsResource( NodeResource ):
    model = Node
    fields = (  'id', 'short_name', 'long_name', 'predecessor', 'etag',
                'subject_count', 'assignment_count', 'period_count', 'subjects', 'breadcrumbs')

    def subjects( self, instance ):
        resource = NodeSubjectResource()
        subjects = Subject.objects.filter( parentnode=instance )
        return resource.serialize_iter( subjects )

    # stats
    def subject_count( self, instance ):
        # [?] does it make recursive calls to the top of the hierarchy? accumulates the sum of all subjects?
        return instance.subjects.count()

    def assignment_count( self, instance ):
        # [?] same problem as the previous method? does it make recursive calls downward the tree?
        result = Period.objects.filter( parentnode__parentnode=instance ).\
        aggregate( Count('assignments')  )
        return result['assignments__count']

    def period_count( self, instance ):
        # [?] downward-recursive?
        result = instance.subjects.all().aggregate( Count('periods') )
        return result['periods__count']


class IsNodeAdmin( BaseIsAdmin ):
    ID_KWARG = 'pk'

    def check_permission( self, user ):
        nodeid = self.get_id()
        nodeadmin_required( user, nodeid )


class RelatedNodeDetails( InstanceModelView ):
    resource = NodeDetailsResource
    permissions = ( IsAuthenticated, IsNodeAdmin, )
    allowed_methods = ('get' ,)


    def get_instance_data( self, instance ):
        return instance


##
# Node Trees
##

class NodeTreeResource( NodeResource ):
    model = Node
    fields = (  'id', 'short_name', 'children', )
    allowed_methods = ('get' ,)

    def children( self, instance ):
        candidates = Node.objects.filter( parentnode=instance )
        return self.serialize_iter( candidates )


class NodeTree( ListModelView ):
    resource = NodeTreeResource
    permissions = (IsAuthenticated, ) # [+] restrict to Admin
    allowed_methods = ('get' ,)

    def get_queryset( self ):
        nodes = Node.where_is_admin_or_superadmin( self.request.user )
        nodes = nodes.exclude( parentnode__in=nodes )
        return nodes




class PathResource( ModelResource ):
    model = Node
    fields = ( 'id', 'path', )

    def path( self, instance ):
        PATH_MAX_LENGTH = 8

        path = []
        counter = 1
        candidate = instance
        candidates = Node.where_is_admin_or_superadmin( self.view.request.user )

        while candidate in candidates and counter < PATH_MAX_LENGTH:
            path.append( candidate )
            candidate = candidate.parentnode
            counter += 1

        path.reverse()

        serializer = PathElementResource()

        return serializer.serialize_iter( path )


class PathElementResource( ModelResource ):
    model = Node
    fields = ( 'id', 'short_name', )

class Path( InstanceModelView ):
    resource = PathResource
    permissions = ( IsAuthenticated, )
    allowed_methods = ('get' ,)