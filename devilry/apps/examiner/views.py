from django.views.generic import TemplateView, View
from django.shortcuts import render
from tempfile import TemporaryFile, NamedTemporaryFile
from devilry.apps.gradeeditors.restful import examiner as gradeeditors_restful
from devilry.utils.module import dump_all_into_dict
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, get_list_or_404
from ..core.models import (Assignment)
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

    def _get_candidates_as_string(self, candidates, assignmentgroup_id):
        candidates_as_string = ""
        size = len(candidates)-1
        for candidate in candidates:
            candidates_as_string += str(candidate)
            if candidate == candidates[size]:
                candidates_as_string += "_"
            else:
                candidates_as_string += "-"
        candidates_as_string += "group-" + str(assignmentgroup_id)
        return candidates_as_string

    def get(self, request, assignmentid):
        assignment = get_object_or_404(Assignment, id=assignmentid)

        zip_file_name = assignment.short_name + ".zip"
        tempfile = NamedTemporaryFile()
        zip_file = zipfile.ZipFile(tempfile, 'w');

        basedir = "deliveries" + os.sep
        path = basedir
                
        for assignmentgroup in assignment.assignmentgroups.all():
            candidates = self._get_candidates_as_string(assignmentgroup.candidates.all(), assignmentgroup.id)

            for deadline in assignmentgroup.deadlines.all():
                deadline_dir_name = deadline.deadline.strftime("%d-%m-%Y_")
                deadline_dir_name += "group-" + str(assignmentgroup.id)
                path += deadline_dir_name + os.sep
                path += candidates + os.sep
                deadline_root = path

                for delivery in deadline.deliveries.all():
                    path += str(delivery.number) + os.sep
                    delivery_root = path

                    for filemeta in delivery.filemetas.all():
                        path += filemeta.filename
                        file_content = filemeta.deliverystore.read_open(filemeta)
                        zip_file.writestr(path, file_content.read())
                        path = delivery_root
                    path = deadline_root
                path = basedir
        zip_file.close()

        tempfile.seek(0)
        response = HttpResponse(FileWrapperWithExplicitClose(tempfile),
                                content_type="application/zip")
        response['Content-Disposition'] = "attachment; filename=%s" % \
            zip_file_name.encode("ascii", 'replace')
        response['Content-Length'] = os.stat(tempfile.name).st_size
        return response
