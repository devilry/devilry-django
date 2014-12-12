from django.views.generic import View
from tempfile import NamedTemporaryFile
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
import zipfile
import os

from devilry.utils.filewrapperwithexplicitclose import FileWrapperWithExplicitClose
from devilry.defaults.encoding import ZIPFILE_FILENAME_CHARSET
from devilry.apps.core.models import Assignment
from devilry.apps.core.models import AssignmentGroup



class DownloadAllDeliveriesOnAssignmentView(View):
    DEADLINE_FORMAT = "%Y-%m-%dT%H_%M_%S"

    def get(self, request, assignmentid):
        assignment = get_object_or_404(
            Assignment.objects.filter_examiner_has_access(self.request.user),
            id=assignmentid)

        zip_rootdir_name = assignment.get_path().encode('ascii', 'replace')
        zip_file_name = '{}.zip'.format(zip_rootdir_name)
        ziptempfile = self._create_zip(assignment, zip_rootdir_name)

        response = HttpResponse(FileWrapperWithExplicitClose(ziptempfile),
                                content_type="application/zip")
        response['Content-Disposition'] = "attachment; filename={}".format(zip_file_name)
        response['Content-Length'] = os.stat(ziptempfile.name).st_size
        return response

    def _create_zip(self, assignment, zip_rootdir_name):
        tempfile = NamedTemporaryFile()
        zip_file = zipfile.ZipFile(tempfile, 'w');

        for group in self._get_queryset(assignment):
            groupname = '{} (groupid={})'.format(group.short_displayname, group.id)
            for deadline in group.deadlines.all():
                for delivery in deadline.deliveries.all():
                    for filemeta in delivery.filemetas.all():
                        file_content = filemeta.deliverystore.read_open(filemeta)
                        filenametpl = '{zip_rootdir_name}/{groupname}/deadline-{deadline}/delivery-{delivery_number}/{filename}'
                        filename = filenametpl.format(
                            zip_rootdir_name=zip_rootdir_name,
                            groupname=groupname,
                            deadline=deadline.deadline.strftime(self.DEADLINE_FORMAT),
                            delivery_number="%.3d" % delivery.number,
                            filename = filemeta.filename.encode(ZIPFILE_FILENAME_CHARSET))
                        zip_file.writestr(filename, file_content.read())
        zip_file.close()

        tempfile.seek(0)
        return tempfile

    def _get_queryset(self, assignment):
        return AssignmentGroup.objects.filter_examiner_has_access(self.request.user)\
            .filter(parentnode=assignment)
