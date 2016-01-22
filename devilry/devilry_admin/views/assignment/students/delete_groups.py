from __future__ import unicode_literals

from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy
from django_cradmin import crapp

from devilry.devilry_admin.views.assignment.students import groupview_base
from devilry.devilry_cradmin import devilry_listbuilder
from devilry.devilry_cradmin import devilry_listfilter


class DeleteGroupsTargetRenderer(devilry_listbuilder.assignmentgroup.GroupTargetRenderer):
    def get_submit_button_text(self):
        return ugettext_lazy('Delete students')

    def get_with_items_title(self):
        return ugettext_lazy('Delete the following students:')


class DeleteGroupsView(groupview_base.BaseMultiselectView):
    filterview_name = 'filter'
    template_name = 'devilry_admin/assignment/students/delete_groups.django.html'

    def add_filterlist_items(self, filterlist):
        filterlist.append(devilry_listfilter.assignmentgroup.SearchNotAnonymous())
        filterlist.append(devilry_listfilter.assignmentgroup.OrderByNotAnonymous())
        filterlist.append(devilry_listfilter.assignmentgroup.StatusRadioFilter(view=self))
        filterlist.append(devilry_listfilter.assignmentgroup.ExaminerFilter(view=self))
        filterlist.append(devilry_listfilter.assignmentgroup.ActivityFilter())

    def get_target_renderer_class(self):
        return DeleteGroupsTargetRenderer

    def has_delete_with_content_permission(self):
        return self.request.cradmin_instance.get_devilryrole_for_requestuser() == 'departmentadmin'

    def get_unfiltered_queryset_for_role(self, role):
        queryset = super(DeleteGroupsView, self).get_unfiltered_queryset_for_role(role=role)
        if self.has_delete_with_content_permission():
            return queryset
        else:
            return queryset\
                .exclude(number_of_groupcomments_from_students__gt=0)\
                .exclude(number_of_imageannotationcomments_from_students__gt=0)\
                .exclude(number_of_groupcomments_from_examiners__gt=0)\
                .exclude(number_of_imageannotationcomments_from_examiners__gt=0)\
                .exclude(number_of_published_feedbacksets__gt=0)

    def form_valid(self, form):
        messages.warning(
            self.request,
            'Merge groups is not finished')
        return redirect(self.request.get_full_path())

    def get_context_data(self, **kwargs):
        context = super(DeleteGroupsView, self).get_context_data(**kwargs)
        context['has_delete_with_content_permission'] = self.has_delete_with_content_permission()
        return context


class App(crapp.App):
    appurls = [
        crapp.Url(r'^$',
                  DeleteGroupsView.as_view(),
                  name=crapp.INDEXVIEW_NAME),
        crapp.Url(r'^filter/(?P<filters_string>.+)?$',
                  DeleteGroupsView.as_view(),
                  name='filter'),
    ]
