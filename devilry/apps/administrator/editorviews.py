from django.views.generic import View
from django.shortcuts import render
from django.http import HttpResponseBadRequest

import restful


class RestfulSimplifiedEditorView(View):
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
                         self.restful.__name__: self.restful}
        return render(request, self.template_name, templatevars)



class NodeEditor(RestfulSimplifiedEditorView):
    template_name = 'administrator/editors/node.django.html'
    restful = restful.RestfulSimplifiedNode



class PeriodEditor(RestfulSimplifiedEditorView):
    template_name = 'administrator/editors/period.django.html'
    restful = restful.RestfulSimplifiedPeriod
