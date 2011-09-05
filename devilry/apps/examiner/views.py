from django.views.generic import TemplateView, View
from django.shortcuts import render
from tempfile import TemporaryFile, NamedTemporaryFile
from devilry.apps.gradeeditors.restful import examiner as gradeeditors_restful
from devilry.utils.module import dump_all_into_dict
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, get_list_or_404
from ..core.models import (Assignment, AssignmentGroup)
from devilry.utils.filewrapperwithexplicitclose import FileWrapperWithExplicitClose
import zipfile
import tarfile
import os, glob
import shutil
import restful


class MainView(TemplateView):
    template_name='examiner/main.django.html'

    def get_context_data(self):
        context = super(MainView, self).get_context_data()
        context['restfulapi'] = dump_all_into_dict(restful);
        return context


class AssignmentGroupView(View):
    def get(self, request, assignmentgroupid):
        context = {'objectid': assignmentgroupid,
                   'restfulapi': dump_all_into_dict(restful),
                   'gradeeditors': dump_all_into_dict(gradeeditors_restful)
                  }
        return render(request,
                      'examiner/assignmentgroupview.django.html',
                       context)

class AssignmentView(View):
    def get(self, request, assignmentid):
        context = {'assignmentid': assignmentid,
                   'restfulapi': dump_all_into_dict(restful),
                   'gradeeditors': dump_all_into_dict(gradeeditors_restful)
                  }
        return render(request,
                      'examiner/assignment.django.html',
                       context) 

                       
class CompressedFileDownloadView(View):

    def _get_candidates_as_string(self, assignmentgroup):
        return '-'.join([candidate.identifier for candidate in assignmentgroup.candidates.all()])

    def get(self, request, assignmentid):
        assignment = get_object_or_404(Assignment, id=assignmentid)
        zip_rootdir_name = assignment.get_path()
        zip_file_name = zip_rootdir_name + ".zip"
        ziptempfile = self._create_zip(request, assignment, zip_rootdir_name)

        response = HttpResponse(FileWrapperWithExplicitClose(ziptempfile),
                                content_type="application/zip")
        response['Content-Disposition'] = "attachment; filename=%s" % \
                zip_file_name.encode("ascii", 'replace')
        response['Content-Length'] = os.stat(ziptempfile.name).st_size
        return response

    def _create_zip(self, request, assignment, zip_rootdir_name):
        tempfile = NamedTemporaryFile()
        zip_file = zipfile.ZipFile(tempfile, 'w');

        for assignmentgroup in self._create_assignment_group_qry(request, assignment):
            candidates = self._get_candidates_as_string(assignmentgroup)

            for deadline in assignmentgroup.deadlines.all():
                for delivery in deadline.deliveries.all():
                    for filemeta in delivery.filemetas.all():
                        file_content = filemeta.deliverystore.read_open(filemeta)
                        filenametpl = '{zip_rootdir_name}/group-{groupid}_{candidates}/deadline-{deadline}/delivery-{delivery_number}/{filename}'
                        filename = filenametpl.format(zip_rootdir_name=zip_rootdir_name,
                                                      groupid=assignmentgroup.id,
                                                      candidates=candidates,
                                                      deadline=deadline.deadline.strftime("%d-%m-%Y"),
                                                      delivery_number=delivery.number,
                                                      filename = filemeta.filename)
                        zip_file.writestr(filename, file_content.read())
        zip_file.close()

        tempfile.seek(0)
        return tempfile

    def _create_assignment_group_qry(self, request, assignment):
        return AssignmentGroup.published_where_is_examiner(request.user, old=False).filter(parentnode=assignment)
