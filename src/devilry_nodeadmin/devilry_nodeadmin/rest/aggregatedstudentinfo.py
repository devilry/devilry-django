from simple_rest import Resource
from simple_rest.response import RESTfulResponse
from devilry_rest.auth import authentication_required
from django.db.models import Q

from devilry.apps.core.models import Node
from devilry.apps.core.models import Candidate
from devilry.apps.core.models import RelatedStudent



@authentication_required
class AggregatedStudentInfo(Resource):
    @RESTfulResponse()
    def get(self, request, user_id, **kwargs):
        data = ['Hello', 'world']
        user_obj = self.request.user
        nodepks_where_is_admin = Node._get_nodepks_where_isadmin(user_obj)
        qry = Candidate.objects.filter(student_id=user_id)
        qry = qry.filter(
                Q(assignment_group__parentnode__admins=user_obj) | \
                Q(assignment_group__parentnode__parentnode__admins=user_obj) | \
                Q(assignment_group__parentnode__parentnode__parentnode__admins=user_obj) | \
                Q(assignment_group__parentnode__parentnode__parentnode__parentnode__pk__in=nodepks_where_is_admin))
        for candidate in qry:
            print candidate
        return data
