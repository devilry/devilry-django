from django.views.generic import DetailView
from django.views.generic import TemplateView
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from devilry.apps.core.models import Assignment
from devilry.apps.core.models import AssignmentGroup


def get_paginated_page(paginator, page):
    try:
        paginated_page = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        paginated_page = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        paginated_page = paginator.page(paginator.num_pages)

    return paginated_page


class AllGroupsOverview(DetailView):
    template_name = "devilry_examiner/allgroupsoverview_base.django.html"
    model = Assignment
    context_object_name = 'assignment'
    pk_url_kwarg = 'assignmentid'

    def get_context_data(self, **kwargs):
        context = super(AllGroupsOverview, self).get_context_data(**kwargs)

        # Need to get queryset from custom manager.
        # Get only AssignmentGroup within same assignment
        groups = AssignmentGroup.objects.get_queryset().filter(parentnode__id=self.object.id)
        groups = groups.filter_examiner_has_access(self.request.user)

        context['groups'] = groups
        return context

    def get_queryset(self):
        return Assignment.objects.filter_examiner_has_access(self.request.user)


class WaitingForFeedbackOverview(AllGroupsOverview):
    template_name = "devilry_examiner/waiting-for-feedback-list.django.html"

    def get_context_data(self, **kwargs):
        context = super(WaitingForFeedbackOverview, self).get_context_data(**kwargs)

        groups = context['groups']
        groups = groups.filter_by_status('waiting-for-something')
        paginator = Paginator(groups, 2, orphans=2)

        page = self.request.GET.get('page')

        context['groups'] = get_paginated_page(paginator, page)

        return context
