from devilry.restful import RestfulManager, RestView, RestfulResult, restful_api

example_restful = RestfulManager()

@example_restful.register
@restful_api
class RestfulExample(RestView):

    def crud_create(self, request, id):
        # Create something here...
        return RestfulResult(dict(message="Successfully created something"))

    def crud_read(self, request, id):
        # A real application would probably get data from the database
        # using the given ``id`` here
        result = dict(data="Hello world", id=id)
        return RestfulResult(result)

    def crud_update(self, request):
        return RestfulResult('Updating')

    def crud_delete(self, request):
        return RestfulResult('Deleting')

    def crud_search(self, request):
        return RestfulResult(['Hello', 'Cruel', 'World'])
