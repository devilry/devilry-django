from django.http import HttpResponse
from django.views.generic import View


class AllApprovedView(View):

    def get(self, request, status):
        return HttpResponse('We are not implemented this plugin')
