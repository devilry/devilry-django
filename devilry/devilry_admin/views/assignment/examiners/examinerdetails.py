from __future__ import unicode_literals

from django_cradmin import crapp

from devilry.devilry_admin.views.assignment.examiners import base_single_examinerview
from devilry.devilry_admin.views.assignment.students import groupview_base


class ExaminerDetailsView(groupview_base.BaseInfoView,
                          base_single_examinerview.SingleExaminerViewMixin):
    filterview_name = crapp.INDEXVIEW_NAME
    template_name = 'devilry_admin/assignment/examiners/examinerdetails.django.html'

    def get_unfiltered_queryset_for_role(self, role):
        return super(ExaminerDetailsView, self).get_unfiltered_queryset_for_role(role=role)\
            .filter(examiners__relatedexaminer=self.get_relatedexaminer())

    def get_filterlist_url(self, filters_string):
        return self.request.cradmin_app.reverse_appurl(
            crapp.INDEXVIEW_NAME,
            kwargs={'filters_string': filters_string,
                    'relatedexaminer_id': self.get_relatedexaminer_id()})

    def get_context_data(self, **kwargs):
        context = super(ExaminerDetailsView, self).get_context_data(**kwargs)
        context['relatedexaminer'] = self.get_relatedexaminer()
        return context


class App(crapp.App):
    appurls = [
        crapp.Url(r'^(?P<relatedexaminer_id>\d+)/(?P<filters_string>.+)?$',
                  ExaminerDetailsView.as_view(),
                  name=crapp.INDEXVIEW_NAME),
    ]
