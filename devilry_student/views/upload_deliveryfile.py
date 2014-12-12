import json
from django.http import HttpResponse
from django.views.generic import View

from devilry.apps.core.models import Deadline
from devilry_student.models import UploadedDeliveryFile




def serialize_uploadedfile(uploaded_deliveryfile):
    return {
        'id': uploaded_deliveryfile.id,
        'filename': uploaded_deliveryfile.filename
    }


class UploadDeliveryFile(View):
    """
    Implements multifile upload of UploadedDeliveryFile.
    """
    def _create_uploaded_deliveryfile(self, djangofileobj, deadline):
        return UploadedDeliveryFile.objects.create_with_file(
            user=self.request.user,
            deadline=deadline,
            filename=UploadedDeliveryFile.prepare_filename(djangofileobj.name),
            filecontent=djangofileobj
        )

    def _error_response(self, error):
        return HttpResponse(json.dumps({
            'success': False,
            'error': error
        }))

    def post(self, request, deadline_id):
        if not request.user.is_authenticated():
            return HttpResponse(status=401)
        try:
            deadline = Deadline.objects\
                .filter(id=deadline_id)\
                .select_related('assignment_group').get()
        except Deadline.DoesNotExist:
            return self._error_response('Deadline not found.')
        else:
            if not deadline.assignment_group.candidates.filter(student=self.request.user).exists():
                return self._error_response('User not Candidate on requested group.')

        if self.request.FILES == None:
            self._error_response('Must have files attached.')
        files = self.request.FILES.getlist(u'files')
        if files:
            uploads = []
            for djangofileobj in files:
                uploaded_deliveryfile = self._create_uploaded_deliveryfile(
                    djangofileobj, deadline)
                uploads.append(serialize_uploadedfile(uploaded_deliveryfile))
            return HttpResponse(json.dumps({
                'success': True,
                'uploads': uploads
            }))
        else:
            return self._error_response('No files attached.')