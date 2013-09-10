from simple_rest import Resource
from simple_rest.response import RESTfulResponse
from devilry_rest.auth import authentication_required




@authentication_required
class AggregatedStudentInfo(Resource):
    @RESTfulResponse()
    def get(self, request, **kwargs):
        data = ['Hello', 'world']
        return data
