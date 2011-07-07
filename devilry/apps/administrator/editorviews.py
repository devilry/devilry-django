from django.views.generic import View
from django.shortcuts import render
from django.http import HttpResponseBadRequest
from django.conf.urls.defaults import url
from django.contrib.auth.decorators import login_required

import restful


class RestfulSimplifiedEditorView(View):
    template_name = 'administrator/editors/base.django.html'

    def get(self, request, id=None):
        record_id = None
        if id == None:
            initial_mode = 'overview'
        elif id.isdigit():
            record_id = int(id)
            initial_mode = 'update'
        elif id != 'create':
            return HttpResponseBadRequest('Requires create or a digit as last url path segment.')
        else:
            initial_mode = 'create'
        templatevars =  {'record_id': record_id,
                         'initial_mode': initial_mode,
                         'RestfulSimplifiedClass': self.restful}
        return render(request, self.template_name, templatevars)

    @classmethod
    def create_url(cls):
        prefix = cls.__name__.replace('Editor', '').lower()
        return url(r'^editors/{0}/(?P<id>\w+)?'.format(prefix),
                   login_required(cls.as_view()),
                   name='administrator-editors-{0}'.format(prefix))


class NodeEditor(RestfulSimplifiedEditorView):
    restful = restful.RestfulSimplifiedNode

class SubjectEditor(RestfulSimplifiedEditorView):
    restful = restful.RestfulSimplifiedSubject

class PeriodEditor(RestfulSimplifiedEditorView):
    restful = restful.RestfulSimplifiedPeriod

class AssignmentEditor(RestfulSimplifiedEditorView):
    restful = restful.RestfulSimplifiedAssignment

class AssignmentGroupEditor(RestfulSimplifiedEditorView):
    restful = restful.RestfulSimplifiedAssignmentGroup

class DeliveryEditor(RestfulSimplifiedEditorView):
    restful = restful.RestfulSimplifiedDelivery
