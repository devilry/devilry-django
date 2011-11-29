from mimetypes import guess_type

from django.views.generic import View
from django.http import HttpResponse, HttpResponseBadRequest



class SaveAs(View):
    def get(self, request):
        return self.download_file(request.GET)

    def post(self, request):
        return self.download_file(request.POST)

    def download_file(self, indata):
        filename = indata.get('filename')
        filecontent = indata.get('content')
        if not (filename and filecontent):
            return HttpResponseBadRequest('"filename" and ""content" are required parameters.')
        filename = filename.encode("ascii", 'replace')
        content_type = indata.get('content_type', guess_type(filename)[0])
        response = HttpResponse(filecontent,
                                content_type=content_type)
        response['Content-Disposition'] = "attachment; filename={filename}".format(filename=filename)
        response['Content-Length'] = len(filecontent)
        return response


class Open(View):
    def get(self, request):
        return self.open_file(request.GET)

    def post(self, request):
        return self.open_file(request.POST)

    def open_file(self, indata):
        filecontent = indata.get('content')
        content_type = indata.get('content_type')
        if not (filecontent and content_type):
            return HttpResponseBadRequest('"content_type" and ""content" are required parameters.')
        response = HttpResponse(filecontent,
                                content_type=content_type)
        response['Content-Length'] = len(filecontent)
        return response
