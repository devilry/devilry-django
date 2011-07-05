from django.views.generic import View
from django.shortcuts import render
from django.http import HttpResponseBadRequest

import restful


class RestfulSimplifiedEditorView(View):
    def get(self, request, initial_mode, id=None):
        if initial_mode == 'update' and id == None:
            return HttpResponseBadRequest('Can not use update as initial mode with no id.')
        templatevars =  {'record_id': id,
                         'initial_mode': initial_mode,
                         self.restful.__name__: self.restful}
        return render(request, self.template_name, templatevars)



class NodeEditor(RestfulSimplifiedEditorView):
    template_name = 'administrator/editors/node.django.html'
    restful = restful.RestfulSimplifiedNode



class PeriodEditor(RestfulSimplifiedEditorView):
    template_name = 'administrator/editors/period.django.html'
    restful = restful.RestfulSimplifiedPeriod
