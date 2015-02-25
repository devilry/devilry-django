from mimetypes import guess_type

from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.views.generic import View

from devilry.devilry_gradingsystem.models import FeedbackDraftFile


class DownloadFeedbackDraftFileView(View):
    def get(self, request, pk, asciifilename=None):
        draftfile = get_object_or_404(FeedbackDraftFile, pk=pk)
        if self.request.user.is_superuser or draftfile.saved_by == self.request.user:
            response = HttpResponse(
                draftfile.file,
                content_type=guess_type(draftfile.filename)[0])
            if 'download' in self.request.GET:
                response['Content-Disposition'] = "attachment; filename={}".format(
                    draftfile.get_ascii_filename())
            return response
        else:
            return HttpResponseForbidden()
