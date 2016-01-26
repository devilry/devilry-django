from __future__ import unicode_literals

from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy, ungettext_lazy
from django_cradmin import crapp

from devilry.apps.core.models import RelatedExaminer, Candidate, Examiner
from devilry.devilry_admin.views.assignment.students import groupview_base
from devilry.devilry_cradmin import devilry_listbuilder


class OrganizeManuallyTargetRenderer(devilry_listbuilder.assignmentgroup.GroupTargetRenderer):
    def get_submit_button_text(self):
        return ugettext_lazy('Add students')


class OrganizeManuallyView(groupview_base.BaseMultiselectView):
    template_name = 'devilry_admin/assignment/examiners/organize_manually/view.django.html'

    # def add_filterlist_items(self, filterlist):
    #     filterlist.append(devilry_listfilter.assignmentgroup.SearchNotAnonymous())
    #     filterlist.append(devilry_listfilter.assignmentgroup.OrderByNotAnonymous())
    #     filterlist.append(devilry_listfilter.assignmentgroup.StatusSelectFilter())
    #     filterlist.append(devilry_listfilter.assignmentgroup.ExaminerFilter(view=self))
    #     filterlist.append(devilry_listfilter.assignmentgroup.ActivityFilter())

    def dispatch(self, request, *args, **kwargs):
        self.relatedexaminer = self.__get_relatedexaminer()
        return super(OrganizeManuallyView, self).dispatch(request, *args, **kwargs)

    def __get_relatedexaminer_id(self):
        return self.kwargs['relatedexaminer_id']

    def __get_relatedexaminer_queryset(self):
        assignment = self.request.cradmin_role
        period = assignment.period
        queryset = RelatedExaminer.objects\
            .filter(period=period)\
            .select_related('user')\
            .annotate_with_number_of_groups_on_assignment(assignment=assignment)\
            .extra_annotate_with_number_of_candidates_on_assignment(assignment=assignment)\
            .exclude(active=False)
        return queryset

    def __get_relatedexaminer(self):
        try:
            return self.__get_relatedexaminer_queryset().get(id=self.__get_relatedexaminer_id())
        except RelatedExaminer.DoesNotExist:
            raise Http404()

    def get_target_renderer_class(self):
        return OrganizeManuallyTargetRenderer

    def get_filterlist_url(self, filters_string):
        return self.request.cradmin_app.reverse_appurl(
            'organize-manually',
            kwargs={'filters_string': filters_string,
                    'relatedexaminer_id': self.__get_relatedexaminer_id()})

    def get_unfiltered_queryset_for_role(self, role):
        return super(OrganizeManuallyView, self).get_unfiltered_queryset_for_role(role=role)\
            .exclude(examiners__relatedexaminer=self.relatedexaminer)

    def get_context_data(self, **kwargs):
        context = super(OrganizeManuallyView, self).get_context_data(**kwargs)
        context['relatedexaminer'] = self.relatedexaminer
        return context

    def get_success_message(self, groupcount, candidatecount):
        if groupcount == candidatecount:
            return ugettext_lazy('Added %(count)s students.') % {
                'count': candidatecount
            }
        else:
            return ungettext_lazy(
                'Added %(groupcount)s project group with %(studentcount)s students.',
                'Added %(groupcount)s project groups with %(studentcount)s students.',
                groupcount
            ) % {
                'groupcount': groupcount,
                'studentcount': candidatecount
            }

    def __create_examiner_objects(self, groupqueryset):
        examiners = []
        groupcount = 0
        candidatecount = 0
        for group in groupqueryset:
            examiner = Examiner(assignmentgroup=group,
                                relatedexaminer=self.relatedexaminer)
            examiners.append(examiner)
            groupcount += 1
            candidatecount += len(group.candidates.all())
        Examiner.objects.bulk_create(examiners)
        return groupcount, candidatecount

    def form_valid(self, form):
        groupqueryset = form.cleaned_data['selected_items']
        groupcount, candidatecount = self.__create_examiner_objects(groupqueryset=groupqueryset)
        messages.success(self.request, self.get_success_message(
            groupcount=groupcount, candidatecount=candidatecount))
        return redirect(self.request.get_full_path())


class App(crapp.App):
    appurls = [
        crapp.Url(r'^(?P<relatedexaminer_id>\d+)/(?P<filters_string>.+)?$',
                  OrganizeManuallyView.as_view(),
                  name='organize-manually'),
    ]
