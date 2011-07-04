from django.views.generic import View
from django.shortcuts import render
from django.http import HttpResponseBadRequest

import restful

class NodeEditor(View):
    def get(self, request, id=None):
        if id == None:
            mode = "browse"
        elif id == "create":
            mode = "create"
        elif id.isdigit():
            mode = "edit"
        else:
            return HttpResponseBadRequest()
        templatevars =  {'record_id': id,
                         'mode': mode,
                         'RestfulSimplifiedNode': restful.RestfulSimplifiedNode}
        return render(request, 'administrator/editors/node.django.html', templatevars)
