

from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy, ngettext_lazy
from cradmin_legacy import crapp

from devilry.apps.core.models import Examiner
from devilry.devilry_admin.views.assignment.examiners import base_single_examinerview
from devilry.devilry_admin.views.assignment.students import groupview_base
from devilry.devilry_cradmin import devilry_listbuilder


class TargetRenderer(devilry_listbuilder.assignmentgroup.GroupTargetRenderer):
    def get_submit_button_text(self):
        return gettext_lazy('Remove students')


class RemoveGroupsToExaminerView(groupview_base.BaseMultiselectView,
                                 base_single_examinerview.SingleExaminerViewMixin):
    template_name = 'devilry_admin/assignment/examiners/remove_groups_from_examiner.django.html'

    def get(self, request, *args, **kwargs):
        response = super(RemoveGroupsToExaminerView, self).get(request, *args, **kwargs)
        if self.get_unfiltered_queryset_for_role(role=self.request.cradmin_role).exists():
            return response
        else:
            messages.info(self.request,
                          gettext_lazy('No students to remove.'))
            return redirect(str(self.get_success_url()))

    def get_target_renderer_class(self):
        return TargetRenderer

    def get_filterlist_url(self, filters_string):
        return self.request.cradmin_app.reverse_appurl(
            crapp.INDEXVIEW_NAME,
            kwargs={'filters_string': filters_string,
                    'relatedexaminer_id': self.get_relatedexaminer_id()})

    def get_unfiltered_queryset_for_role(self, role):
        return super(RemoveGroupsToExaminerView, self).get_unfiltered_queryset_for_role(role=role)\
            .filter(examiners__relatedexaminer=self.get_relatedexaminer())

    def get_context_data(self, **kwargs):
        context = super(RemoveGroupsToExaminerView, self).get_context_data(**kwargs)
        context['relatedexaminer'] = self.get_relatedexaminer()
        return context

    def get_success_message(self, groupcount, candidatecount):
        if groupcount == candidatecount:
            return gettext_lazy('Removed %(count)s students.') % {
                'count': candidatecount
            }
        else:
            return ngettext_lazy(
                'Removed %(groupcount)s project group with %(studentcount)s students.',
                'Removed %(groupcount)s project groups with %(studentcount)s students.',
                groupcount
            ) % {
                'groupcount': groupcount,
                'studentcount': candidatecount
            }

    def __remove_examiner_objects(self, groupqueryset):
        groupcount = 0
        candidatecount = 0
        for group in groupqueryset:
            groupcount += 1
            candidatecount += len(group.candidates.all())
        examinerqueryset = Examiner.objects\
            .filter(assignmentgroup__in=groupqueryset,
                    relatedexaminer=self.get_relatedexaminer())
        examinerqueryset.delete()
        return groupcount, candidatecount

    def get_success_url(self):
        return self.request.cradmin_instance.reverse_url(
            appname='examinerdetails',
            viewname=crapp.INDEXVIEW_NAME,
            kwargs={'relatedexaminer_id': self.get_relatedexaminer_id()})

    def form_valid(self, form):
        groupqueryset = form.cleaned_data['selected_items']
        groupcount, candidatecount = self.__remove_examiner_objects(groupqueryset=groupqueryset)
        messages.success(self.request, self.get_success_message(
            groupcount=groupcount, candidatecount=candidatecount))
        return redirect(str(self.get_success_url()))


class App(crapp.App):
    appurls = [
        crapp.Url(r'^(?P<relatedexaminer_id>\d+)/(?P<filters_string>.+)?$',
                  RemoveGroupsToExaminerView.as_view(),
                  name=crapp.INDEXVIEW_NAME),
    ]
