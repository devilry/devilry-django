from tempfile import NamedTemporaryFile
import zipfile
from os import stat
from mimetypes import guess_type
import posixpath

from django.views.generic import View
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden
from django.core.servers.basehttp import FileWrapper

from devilry.apps.core.models import Delivery, FileMeta
from devilry.utils.filewrapperwithexplicitclose import FileWrapperWithExplicitClose


class FileDownloadView(View):

    def get(self, request, filemetaid):    
        filemeta = get_object_or_404(FileMeta, id=filemetaid)
        assignment_group = filemeta.delivery.deadline.assignment_group
        if not (assignment_group.is_candidate(request.user) \
                    or assignment_group.is_examiner(request.user) \
                    or request.user.is_superuser \
                    or assignment_group.parentnode.is_admin(request.user)):
            return HttpResponseForbidden("Forbidden")
        
        # TODO: make this work on any storage backend
        response = HttpResponse(FileWrapper(filemeta.deliverystore.read_open(filemeta)),
                                content_type=guess_type(filemeta.filename)[0])
        response['Content-Disposition'] = "attachment; filename=%s" % \
            filemeta.filename.encode("ascii", 'replace')
        response['Content-Length'] = filemeta.size

        return response


class CompressedFileDownloadView(View):

    def get(self, request, deliveryid):
        delivery = get_object_or_404(Delivery, id=deliveryid)
        assignment_group = delivery.deadline.assignment_group
        if not (assignment_group.is_candidate(request.user) \
                    or assignment_group.is_examiner(request.user) \
                    or request.user.is_superuser \
                    or assignment_group.parentnode.is_admin(request.user)):
            return HttpResponseForbidden("Forbidden")
        dirname = u'{}-{}-delivery{}'.format(
                assignment_group.parentnode.get_path(),
                assignment_group.short_displayname,
                delivery.number)
        zip_file_name = u'{}.zip'.format(dirname.encode('ascii', 'ignore'))

        tempfile = NamedTemporaryFile()
        zip_file = zipfile.ZipFile(tempfile, 'w');

        for filemeta in delivery.filemetas.all():
            file_content = filemeta.deliverystore.read_open(filemeta)
            zip_file.write(file_content.name, posixpath.join(dirname, filemeta.filename))
        zip_file.close()

        tempfile.seek(0)
        response = HttpResponse(FileWrapperWithExplicitClose(tempfile),
                                content_type="application/zip")
        response['Content-Disposition'] = "attachment; filename=%s" % \
            zip_file_name.encode("ascii", 'replace')
        response['Content-Length'] = stat(tempfile.name).st_size
        return response
