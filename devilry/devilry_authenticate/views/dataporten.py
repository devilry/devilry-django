from django.http import HttpResponse
from django.views.generic import View


class DataportenOauthRedirectView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse('SUCCESS!')
