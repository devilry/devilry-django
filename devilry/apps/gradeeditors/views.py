from django.views.generic import View
from django.http import HttpResponseRedirect


class LoadGradeEditor(View):
    def get(self, request, assignmentid):
        # TODO: Load assignment and find correct grade editor
        return HttpResponseRedirect('/static/gradeeditors/approved.js')
