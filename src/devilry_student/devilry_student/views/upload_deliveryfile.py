import json
from os.path import splitext
from os.path import basename
from simple_rest import Resource
from simple_rest.auth.decorators import login_required
from django.http import HttpResponse

from devilry.apps.core.models import Deadline
from devilry_student.models import UploadedDeliveryFile




def serialize_uploadedfile(uploaded_deliveryfile):
    return {
        'id': uploaded_deliveryfile.id,
        'filename': uploaded_deliveryfile.filename
    }


class UploadDeliveryFile(Resource):
    """
    Implements multifile upload of UploadedDeliveryFile.

    .. note::

        We use django-simple-rest mainly because we want 401 instead of 302
        on missing authentication. We could easily replace this with a standard
        Django view, but we will most likely want to support API keys with this
        view, so it makes sense to use django simple rest.
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

    @login_required
    def post(self, request, deadline_id):
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