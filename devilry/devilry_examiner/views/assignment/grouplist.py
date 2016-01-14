from __future__ import unicode_literals

from django.db import models
from django.db.models.functions import Lower, Concat
from django.utils.translation import ugettext_lazy, pgettext_lazy
from django_cradmin import crapp
from django_cradmin.crinstance import reverse_cradmin_url
from django_cradmin.viewhelpers import listbuilder
from django_cradmin.viewhelpers import listbuilderview
from django_cradmin.viewhelpers import listfilter

from devilry.apps.core import models as coremodels
from devilry.apps.core.models import Candidate
from devilry.devilry_cradmin import devilry_listfilter


class GroupItemValue(listbuilder.itemvalue.TitleDescription):
    valuealias = 'group'
    template_name = 'devilry_examiner/assignment/itemvalue/group-item-value.django.html'

    def get_candidate_users(self):
        return [candidate.relatedstudent.user for candidate in self.group.candidates.all()]

    def get_description(self):
        return ''

    # def get_extra_css_classes_list(self):
    #     css_classes = ['devilry-examiner-listbuilder-assignmentlist-assignmentitemvalue']
    #     if self.group.waiting_for_feedback_count > 0:
    #         css_classes.append('devilry-django-cradmin-listbuilder-itemvalue-titledescription-description-warning')
    #     else:
    #         css_classes.append('devilry-django-cradmin-listbuilder-itemvalue-titledescription-description-muted')
    #     return css_classes


class GroupItemFrame(listbuilder.itemframe.Link):
    valuealias = 'group'

    def get_url(self):
        return reverse_cradmin_url(
            instanceid='devilry_group_examiner',
            appname='feedbackfeed',
            roleid=self.group.id,
            viewname=crapp.INDEXVIEW_NAME,
        )


class GroupListView(listbuilderview.FilterListMixin,
                    listbuilderview.View):
    model = coremodels.AssignmentGroup
    value_renderer_class = GroupItemValue
    frame_renderer_class = GroupItemFrame

    def dispatch(self, request, *args, **kwargs):
        self.assignment = self.request.cradmin_role
        return super(GroupListView, self).dispatch(request, *args, **kwargs)

    def get_filterlist_template_name(self):
        return 'devilry_examiner/assignment/grouplist.django.html'

    def get_pagetitle(self):
        return self.assignment.long_name

    def get_filterlist_url(self, filters_string):
        return self.request.cradmin_app.reverse_appurl(
            'filter',
            kwargs={'filters_string': filters_string})

    def __add_filterlist_items_anonymous_uses_custom_candidate_ids(self, filterlist):
        filterlist.append(devilry_listfilter.assignmentgroup.SearchAnonymousUsesCustomCandidateIds())
        filterlist.append(devilry_listfilter.assignmentgroup.OrderByAnonymousUsesCustomCandidateIds())

    def __add_filterlist_items_anonymous(self, filterlist):
        filterlist.append(devilry_listfilter.assignmentgroup.SearchAnonymous())
        filterlist.append(devilry_listfilter.assignmentgroup.OrderByAnonymous())

    def __add_filterlist_items_not_anonymous(self, filterlist):
        filterlist.append(devilry_listfilter.assignmentgroup.SearchNotAnonymous())
        filterlist.append(devilry_listfilter.assignmentgroup.OrderByNotAnonymous())

    def add_filterlist_items(self, filterlist):
        if self.assignment.is_anonymous:
            if self.assignment.uses_custom_candidate_ids:
                self.__add_filterlist_items_anonymous_uses_custom_candidate_ids(filterlist=filterlist)
            else:
                self.__add_filterlist_items_anonymous(filterlist=filterlist)
        else:
            self.__add_filterlist_items_not_anonymous(filterlist=filterlist)

    def get_unfiltered_queryset_for_role(self, role):
        assignment = role
        candidatequeryset = Candidate.objects\
            .select_related('relatedstudent')\
            .order_by(
                Lower(Concat('relatedstudent__user__fullname',
                             'relatedstudent__user__shortname')))
        return coremodels.AssignmentGroup.objects\
            .filter_examiner_has_access(user=self.request.user)\
            .filter(parentnode=assignment)\
            .select_related('parentnode')\
            .prefetch_related(
                models.Prefetch('candidates',
                                queryset=candidatequeryset))\
            .annotate_with_grading_points()\
            .distinct()


class App(crapp.App):
    appurls = [
        crapp.Url(r'^$',
                  GroupListView.as_view(),
                  name=crapp.INDEXVIEW_NAME),
        crapp.Url(r'^filter/(?P<filters_string>.+)?$',
                  GroupListView.as_view(),
                  name='filter'),
    ]
