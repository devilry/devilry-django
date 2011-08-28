from django.views.generic import TemplateView, View
from django.shortcuts import render

from devilry.apps.gradeeditors.restful import examiner as gradeeditors_restful
from devilry.utils.module import dump_all_into_dict
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, get_list_or_404
from ..core.models import (Assignment)
import zipfile
import tarfile
import os
import restful


class MainView(TemplateView):
    template_name='examiner/main.django.html'

    def get_context_data(self):
        context = super(MainView, self).get_context_data()
        for restclsname in restful.__all__:
            context[restclsname] = getattr(restful, restclsname)
        context['restfulclasses'] = [getattr(restful, restclsname) for restclsname in restful.__all__]
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

    def _get_candidates_as_string(self, candidates):
        candidates_as_string = ""
        for candidate in candidates:
            candidates_as_string += str(candidate)
            candidates_as_string += "-"
        return candidates_as_string
            
    def get(self, request, assignmentid):
        print "#", assignmentid, "#"
        assignment = get_object_or_404(Assignment, id=assignmentid)
        root = os.getcwd()
        print dir(assignment)
        for assignmentgroup in assignment.assignmentgroups.all():
            print assignmentgroup
            candidates = self._get_candidates_as_string(assignmentgroup.candidates.all())
            candidates += str(assignmentgroup.id)
            
            for deadline in assignmentgroup.deadlines.all():
                deadline_dir = os.getcwd()
                deadline_dir_name = deadline.deadline.strftime("%d-%m-%Y")
                os.mkdir(deadline_dir_name)
                print " ", deadline_dir_name
                os.chdir(os.path.join(os.getcwd(), deadline_dir_name))
                os.mkdir(candidates)
                for delivery in deadline.deliveries.all():
                    delivery_dir = os.getcwd()
                    print "  ", delivery
                    os.chdir(os.path.join(os.getcwd(), candidates))
                    os.mkdir(str(delivery.number))
                    for filemeta in delivery.filemetas.all():
                        filemeta_dir = os.getcwd()
                        os.chdir(os.path.join(os.getcwd(), str(delivery.number)))
                        file_content = filemeta.deliverystore.read_open(filemeta)
                        ut = open(filemeta.filename, 'w')
                        ut.write(file_content.read())
                        ut.close()
                        os.chdir(filemeta_dir)
                        print "   ", filemeta
                    os.chdir(delivery_dir)
                        
                os.chdir(deadline_dir)
        # delivery = get_object_or_404(Delivery, id=deliveryid)
        # zip_file_name = str(delivery.delivered_by) + ".zip"

        # tempfile = TemporaryFile()
        # zip_file = zipfile.ZipFile(tempfile, 'w');

        # for filemeta in delivery.filemetas.all():
            # file_content = filemeta.deliverystore.read_open(filemeta)
            # zip_file.write(file_content.name, filemeta.filename)
        # zip_file.close()

        # tempfile.seek(0)
        # response = HttpResponse(FileWrapperWithExplicitClose(tempfile),
                                # content_type="application/zip")
        # response['Content-Disposition'] = "attachment; filename=%s" % \
            # zip_file_name.encode("ascii", 'replace')
        # response['Content-Length'] = stat(tempfile.name).st_size
        return HttpResponse("Hei Verden")