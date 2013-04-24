from simple_rest import Resource
from simple_rest.auth.decorators import login_required
from simple_rest.response import RESTfulResponse

from devilry_qualifiesforexam.models import Status


@login_required
@RESTfulResponse()
class AdminSummaryResource(Resource):
    def get(self, request, contact_id=None, **kwargs):
        data = ['Hello', 'world']
        #qry = Status.objects.filter(status=Status.READY)
        #print qry.all()
        return data
