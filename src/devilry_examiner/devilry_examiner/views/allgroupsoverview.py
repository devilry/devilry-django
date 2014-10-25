from crispy_forms import layout
from crispy_forms.helper import FormHelper
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect
from django.views.generic import DetailView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic import View
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from django import forms
from django.utils.translation import ugettext_lazy as _

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


class OrderingForm(forms.Form):
    order_by = forms.ChoiceField(
        required=False,
        choices=[
            ('', _('Order by: Name')),
            ('name_descending', _('Order by: Name reversed')),
            ('username', _('Order by: Username')),
            ('username_descending', _('Order by: Username reversed'))
        ]
    )

    def __init__(self, *args, **kwargs):
        super(OrderingForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_method = 'GET'
        self.helper.form_class = 'form-inline'
        self.helper.form_show_labels = False
        self.helper.disable_csrf = True
        self.helper.layout = layout.Layout(
            layout.Field('order_by', onchange="this.form.submit();"),
        )


class AllGroupsOverview(DetailView):
    template_name = "devilry_examiner/allgroupsoverview_base.django.html"
    model = Assignment
    context_object_name = 'assignment'
    pk_url_kwarg = 'assignmentid'
    currentpage = 'all'

    order_by_map = {
        '': 'candidates__student__devilryuserprofile__full_name',
        'name_descending': '-candidates__student__devilryuserprofile__full_name',
        'username': 'candidates__student__username',
        'username_descending': '-candidates__student__username',
    }

    def get(self, *args, **kwargs):
        self.orderingform = OrderingForm(self.request.GET)
        if self.orderingform.is_valid():
            self.order_by = self.orderingform.cleaned_data['order_by']
        else:
            return HttpResponseBadRequest(self.orderingform.errors.as_text())
        return super(AllGroupsOverview, self).get(*args, **kwargs)

    def _order_groupqueryset(self, groupqueryset):
        groupqueryset = groupqueryset.order_by(self.order_by_map[self.order_by])
        return groupqueryset

    def _get_groupqueryset(self):
        # Need to get queryset from custom manager.
        # Get only AssignmentGroup within same assignment
        groupqueryset = AssignmentGroup.objects.get_queryset()\
            .filter(parentnode__id=self.object.id)\
            .filter_examiner_has_access(self.request.user)
        groupqueryset = self._order_groupqueryset(groupqueryset)
        return groupqueryset

    def get_context_data(self, **kwargs):
        if 'selected_group_ids' in self.request.session:
            del self.request.session['selected_group_ids']

        context = super(AllGroupsOverview, self).get_context_data(**kwargs)
        assignment = self.object

        groups = self._get_groupqueryset()
        context['count_all'] = groups.count()
        context['count_waiting_for_feedback'] = groups.filter_waiting_for_feedback().count()
        if assignment.is_electronic:
            context['count_waiting_for_deliveries'] = groups.filter_waiting_for_deliveries().count()
        context['count_corrected'] = groups.filter_by_status('corrected').count()

        paginator = Paginator(groups, 100, orphans=3)
        page = self.request.GET.get('page')

        context['groups'] = get_paginated_page(paginator, page)
        context['allgroups'] = groups
        context['currentpage'] = self.currentpage

        context['orderingform'] = self.orderingform
        context['order_by'] = self.order_by

        return context

    def get_queryset(self):
        return Assignment.objects.filter_examiner_has_access(self.request.user)


class WaitingForFeedbackOverview(AllGroupsOverview):
    template_name = "devilry_examiner/waiting-for-feedback-list.django.html"
    currentpage = 'waiting_for_feedback'

    def get_context_data(self, **kwargs):
        context = super(WaitingForFeedbackOverview, self).get_context_data(**kwargs)

        groups = context['allgroups']
        groups = groups.filter_waiting_for_feedback()
        paginator = Paginator(groups, 100, orphans=2)

        page = self.request.GET.get('page')

        context['groups'] = get_paginated_page(paginator, page)

        return context


class WaitingForDeliveriesOverview(AllGroupsOverview):
    template_name = "devilry_examiner/waiting-for-deliveries-overview.django.html"
    currentpage = 'waiting_for_deliveries'

    def get_context_data(self, **kwargs):
        context = super(WaitingForDeliveriesOverview, self).get_context_data(**kwargs)

        groups = context['allgroups']
        groups = groups.filter_waiting_for_deliveries()
        paginator = Paginator(groups, 100, orphans=2)

        page = self.request.GET.get('page')

        context['groups'] = get_paginated_page(paginator, page)

        return context


class CorrectedOverview(AllGroupsOverview):
    template_name = "devilry_examiner/corrected-overview.django.html"
    currentpage = 'corrected'

    def get_context_data(self, **kwargs):
        context = super(CorrectedOverview, self).get_context_data(**kwargs)

        groups = context['allgroups']
        groups = groups.filter_by_status('corrected')
        paginator = Paginator(groups, 100, orphans=2)

        page = self.request.GET.get('page')

        context['groups'] = get_paginated_page(paginator, page)

        return context



class WaitingForFeedbackOrAllRedirectView(SingleObjectMixin, View):
    model = Assignment
    context_object_name = 'assignment'
    pk_url_kwarg = 'assignmentid'

    def get(self, *args, **kwargs):
        assignment = self.get_object()
        has_waiting_for_feedback = AssignmentGroup.objects\
            .filter_examiner_has_access(self.request.user)\
            .filter(parentnode=assignment)\
            .filter_waiting_for_feedback().exists()
        if has_waiting_for_feedback:
            viewname = 'devilry_examiner_waiting_for_feedback'
        else:
            viewname = 'devilry_examiner_allgroupsoverview'
        return redirect(viewname, assignmentid=assignment.id)

    def get_queryset(self):
        return Assignment.objects.filter_examiner_has_access(self.request.user)
