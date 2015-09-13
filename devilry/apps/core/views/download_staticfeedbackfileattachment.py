from mimetypes import guess_type

from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import View

from devilry.apps.core.models import StaticFeedbackFileAttachment


class DownloadStaticFeedbackFileAttachmentView(View):
    def get(self, request, pk, asciifilename=None):
        if self.request.user.is_superuser:
            queryset = StaticFeedbackFileAttachment.objects.all()
        else:
            queryset = StaticFeedbackFileAttachment.objects \
                .filter(Q(staticfeedback__delivery__deadline__assignment_group__candidates__student=self.request.user) |
                        Q(staticfeedback__delivery__deadline__assignment_group__examiners__user=self.request.user)) \
                .distinct()
        fileattachment = get_object_or_404(queryset, pk=pk)

        response = HttpResponse(
            fileattachment.file,
            content_type=guess_type(fileattachment.filename)[0])
        if 'download' in self.request.GET:
            response['Content-Disposition'] = "attachment; filename={}".format(
                fileattachment.get_ascii_filename())
        return response
