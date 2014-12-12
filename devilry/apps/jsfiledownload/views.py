from mimetypes import guess_type
from xml.sax.saxutils import escape

from django.views.generic import View
from django.http import HttpResponse, HttpResponseBadRequest


class Base(View):
    def get(self, request):
        return self.download_file(request.GET)

    def post(self, request):
        return self.download_file(request.POST)

    def get_filecontent(self, indata):
        filecontent = indata.get('content')
        if not filecontent:
            filecontent = self.request.FILES.get('content')
            if filecontent:
                filecontent = filecontent.read()
        if filecontent and indata.get('xmlescape_content'): # See: http://docs.sencha.com/ext-js/4-0/#!/api/Ext.form.Basic-method-hasUpload
            filecontent = escape(filecontent)
        return filecontent


class SaveAs(Base):
    def download_file(self, indata):
        filename = indata.get('filename')
        filecontent = self.get_filecontent(indata)
        if not (filename and filecontent):
            return HttpResponseBadRequest('"filename" and "content" are required parameters.')
        filename = filename.encode("ascii", 'replace')
        content_type = indata.get('content_type', guess_type(filename)[0])
        response = HttpResponse(filecontent,
                                content_type=content_type)
        response['Content-Disposition'] = "attachment; filename={filename}".format(filename=filename)
        response['Content-Length'] = len(filecontent)
        return response


class Open(Base):
    def download_file(self, indata):
        content_type = indata.get('content_type')
        filecontent = self.get_filecontent(indata)
        if not (filecontent and content_type):
            return HttpResponseBadRequest('"content_type" and "content" are required parameters.')
        response = HttpResponse(filecontent,
                                content_type=content_type)
        response['Content-Length'] = len(filecontent)
        return response
