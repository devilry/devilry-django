from simple_rest import Resource
from simple_rest.response import RESTfulResponse


class AssignmentListing(Resource):
    @RESTfulResponse()
    def get(self, request, **kwargs):
        data = ['Hello', 'world']
        return data
