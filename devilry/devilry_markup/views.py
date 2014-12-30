from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.views.generic import View

from devilry.devilry_markup.parse_markdown import markdown_full


class DevilryFlavouredMarkdownFull(View):

    def _parse(self, data):
        if 'md' in data:
            md = data['md']
            return HttpResponse(markdown_full(md))
        else:
            return HttpResponseBadRequest('"md" not in POST data.')

    def post(self, request):
        return self._parse(request.POST)

    ## For debugging:
    #def get(self, request):
        #return self._parse(request.GET)
