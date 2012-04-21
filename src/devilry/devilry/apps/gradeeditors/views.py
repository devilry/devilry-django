from devilry.restful import (RestfulView, restful_api, SerializableResult,
                             ForbiddenSerializableResult)
from registry import gradeeditor_registry


@restful_api
class RestfulGradeEditorConfig(RestfulView):
    """
    RESTful API to search and read information about items in the gradeeditor registry.
    """
    def crud_read(self, request, id):
        try:
            registryitem = gradeeditor_registry[id]
        except KeyError, e:
            return ForbiddenSerializableResult()
        else:
            return SerializableResult(self.extjswrapshortcut(registryitem.asinfodict()))

    def crud_search(self, request):
        result = list(gradeeditor_registry.iterinfordicts())
        result = self.extjswrapshortcut(result, total=len(result))
        return SerializableResult(result)
