from django.views.generic import View
from django.shortcuts import render

import restful

class NodeEditor(View):
    def get(self, request, id):
        templatevars =  {'id': id,
                         'RestfulSimplifiedNode': restful.RestfulSimplifiedNode}
        return render(request, 'administrator/editors/node.django.html', templatevars)
