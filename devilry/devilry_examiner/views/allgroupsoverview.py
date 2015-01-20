from crispy_forms import layout
from crispy_forms.helper import FormHelper
from django.http import HttpResponseBadRequest
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
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
from devilry.devilry_gradingsystem.models import FeedbackDraft


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
    assignment_type_choices_map = {
        'normal': [
            ('', _('Order by: Name')),
            ('name_descending', _('Order by: Name reversed')),
            # ('lastname', _('Order by: Last name')),
            # ('lastname_descending', _('Order by: Last name reversed')),
            ('username', _('Order by: Username')),
            ('username_descending', _('Order by: Username reversed'))
        ],
        'anonymous':[
            ('candidate_id', _("Order by: Candidate id")),
            ('candidate_id_descending', _("Order by: Candidate id reversed"))
        ],
        }
    order_by = forms.ChoiceField(
        required=False
    )

    def __init__(self, *args, **kwargs):
        assignment_type = kwargs.pop('assignment_type', 'normal')
        super(OrderingForm, self).__init__(*args, **kwargs)
        self.fields['order_by'].choices = self.assignment_type_choices_map[assignment_type]
        self.fields['examinermode'] = forms.CharField(required=False, max_length=50, widget=forms.HiddenInput())
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_method = 'GET'
        self.helper.form_class = 'form-inline'
        self.helper.form_show_labels = False
        self.helper.disable_csrf = True
        self.helper.layout = layout.Layout(
            layout.Field('order_by', onchange="this.form.submit();"),
            layout.Field('examinermode')
        )

class ExaminerModeForm(forms.Form):
    examinermode = forms.ChoiceField(
        required=False,
        choices=[
            ('normal', _('Edit mode: Normal')),
            ('quick', _('Edit mode: Quick'))
        ]
    )

    def __init__(self, *args, **kwargs):
        super(ExaminerModeForm, self).__init__(*args, **kwargs)
        self.fields['order_by'] = forms.CharField(required=False, max_length=50, widget=forms.HiddenInput())
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_method = 'GET'
        self.helper.form_class = 'form-inline'
        self.helper.form_show_labels = False
        self.helper.disable_csrf = True
        self.helper.layout = layout.Layout(
            layout.Field('order_by'),
            layout.Field('examinermode', onchange="this.form.submit();")
        )


class QuickApprovedNotApprovedFeedbackForm(forms.Form):
    points = forms.ChoiceField(
        required=False,
        choices=[
            ('', ''),
            ('1', _('Passed')),
            ('0', _('Failed')),
        ]
    )

    def __init__(self, *args, **kwargs):
        self.group = kwargs.pop('group')
        super(QuickApprovedNotApprovedFeedbackForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.form_show_labels = False
        self.helper.layout = layout.Layout(
            layout.Field('points'),
        )

    def get_draft(self, request):
        points = self.cleaned_data['points']

        if points == '':
            return None
        points = int(points)

        if self.group.last_delivery_id is None:
            return None
        if self.group.feedback and self.group.feedback.points == points:
            return None

        draft = FeedbackDraft(
            delivery_id=self.group.last_delivery_id,
            points=points,
            feedbacktext_raw='',
            feedbacktext_html='',
            saved_by=request.user
        )
        return draft


class QuickFeedbackFormCollection(object):
    def __init__(self, request, assignment, groupqueryset):
        self.request = request
        self.assignment = assignment
        self.groupqueryset = groupqueryset
        self.forms = self._create_forms()

    def _get_form_class(self):
        # TODO: Use assignment to find grading system
        return QuickApprovedNotApprovedFeedbackForm

    def _get_initial(self, feedback):
        # TODO: Use assignment to find grading system
        if feedback is None:
            points = ''
        else:
            points = feedback.points
        return {
            'points': points
        }

    def _create_forms(self):
        form_class = self._get_form_class()
        forms = {}
        for group in self.groupqueryset.all():
            feedback = group.feedback
            kwargs = {
                'group': group,
                'prefix': 'quickfeedbackform{}'.format(group.id),
                'initial': self._get_initial(feedback),
            }
            if self.request.method == 'POST':
                form = form_class(self.request.POST, **kwargs)
            else:
                form = form_class(**kwargs)
            forms[group.id] = form
        return forms

    def get_form_by_groupid(self, groupid):
        return self.forms[groupid]

    def is_valid(self):
        is_valid = True
        for form in self.forms.itervalues():
            if not form.is_valid():
                is_valid = False
        return is_valid

    def save(self):
        for form in self.forms.itervalues():
            draft = form.get_draft(self.request)
            if draft is None:
                continue
            draft.published = True
            draft.staticfeedback = draft.to_staticfeedback()
            draft.staticfeedback.full_clean()
            draft.staticfeedback.save()
            draft.save()


class AllGroupsOverview(DetailView):
    template_name = "devilry_examiner/allgroupsoverview_base.django.html"
    model = Assignment
    context_object_name = 'assignment'
    pk_url_kwarg = 'assignmentid'
    currentpage = 'all'
    paginate_by = 100

    order_by_map = {
        '': 'candidates__student__devilryuserprofile__full_name',
        'name_descending': '-candidates__student__devilryuserprofile__full_name',
        'username': 'candidates__student__username',
        'username_descending': '-candidates__student__username',
        # 'lastname': 'candidates__student__last_name',
        # 'lastname_descending': '-candidates__student__last_name',
        'candidate_id': 'candidates__candidate_id',
        'candidate_id_descending': '-candidates__candidate_id'
    }

    def get_success_url(self):
        query_string = self.request.META.get('QUERY_STRING', '')
        url = "{}?{}".format(reverse('devilry_examiner_allgroupsoverview', args=[self.object.id]), query_string)
        return url

    def _get_assignment_type(self, *args, **kwargs):
        assignmentid = kwargs.get('assignmentid')
        assignment = Assignment.objects.get(id=assignmentid)
        assignment_type = "normal"
        if assignment.anonymous:
            assignment_type = "anonymous"
        return assignment_type

    def dispatch(self, request, *args, **kwargs):
        self.orderingform = OrderingForm(request.GET, assignment_type=self._get_assignment_type(*args, **kwargs))
        self.examinermode_form = ExaminerModeForm(request.GET)
        if self.examinermode_form.is_valid():
            self.examinermode = self.examinermode_form.cleaned_data['examinermode']
            if not self.examinermode:
                self.examinermode = 'normal'
        else:
            return HttpResponseBadRequest(self.examinermode_form.errors.as_text())
        if self.orderingform.is_valid():
            self.order_by = self.orderingform.cleaned_data['order_by']
        else:
            return HttpResponseBadRequest(self.orderingform.errors.as_text())
        return super(AllGroupsOverview, self).dispatch(request, *args, **kwargs)

    def _order_groupqueryset(self, groupqueryset):
        if self.order_by in ('', 'name_descending'):
            if self.order_by == '':
                order_by_field = 'full_name'
            else:
                order_by_field = '-full_name'
            groupqueryset = groupqueryset.extra(
                select={
                    'full_name': """
                        SELECT selected_candidate.selected_candidate_full_name
                        FROM (
                            SELECT
                              core_devilryuserprofile.full_name as selected_candidate_full_name
                            FROM core_candidate
                            INNER JOIN auth_user
                              ON auth_user.id=core_candidate.student_id
                            INNER JOIN core_devilryuserprofile
                              ON core_devilryuserprofile.user_id=auth_user.id
                            WHERE core_assignmentgroup.id=core_candidate.assignment_group_id
                            ORDER BY core_devilryuserprofile.full_name
                            LIMIT 1
                        ) AS selected_candidate
                    """
                },
                order_by=[order_by_field]
            )
        elif self.order_by in ('username', 'username_descending'):
            if self.order_by == 'username':
                order_by_field = 'username'
            else:
                order_by_field = '-username'
            groupqueryset = groupqueryset.extra(
                select={
                    'username': """
                        SELECT selected_candidate.selected_candidate_username
                        FROM (
                            SELECT
                              auth_user.username as selected_candidate_username
                            FROM core_candidate
                            INNER JOIN auth_user
                              ON auth_user.id=core_candidate.student_id
                            WHERE core_assignmentgroup.id=core_candidate.assignment_group_id
                            ORDER BY auth_user.username
                            LIMIT 1
                        ) AS selected_candidate
                    """
                },
                order_by=[order_by_field]
            )
        elif self.order_by in ('candidate_id', 'candidate_id_descending'):
            if self.order_by == 'candidate_id':
                order_by_field = 'candidate_id'
            else:
                order_by_field = '-candidate_id'
            groupqueryset = groupqueryset.extra(
                select={
                    'candidate_id': """
                        SELECT selected_candidate.selected_candidate_id
                        FROM (
                            SELECT
                              core_candidate.candidate_id as selected_candidate_id
                            FROM core_candidate
                            WHERE core_assignmentgroup.id=core_candidate.assignment_group_id
                            ORDER BY core_candidate.candidate_id
                            LIMIT 1
                        ) AS selected_candidate
                    """
                },
                order_by=[order_by_field]
            )
        return groupqueryset

    def _get_groupqueryset(self):
        # Need to get queryset from custom manager.
        # Get only AssignmentGroup within same assignment
        groupqueryset = AssignmentGroup.objects.get_queryset()\
            .filter(parentnode__id=self.object.id)\
            .filter_examiner_has_access(self.request.user)\
            .annotate_with_last_delivery_id()
        groupqueryset = self._order_groupqueryset(groupqueryset)
        return groupqueryset

    def _get_paginator(self, groups):
        return Paginator(groups, self.paginate_by, orphans=3)

    def get_context_data(self, **kwargs):
        if 'selected_group_ids' in self.request.session:
            del self.request.session['selected_group_ids']

        context = super(AllGroupsOverview, self).get_context_data(**kwargs)
        assignment = self.object

        if 'quickfeedback_formcollection' not in context:
            context['quickfeedback_formcollection'] = self._get_quickfeedback_formcollection()

        groups = self._get_groupqueryset()
        context['count_all'] = groups.count()
        context['count_waiting_for_feedback'] = groups.filter_waiting_for_feedback().count()
        if assignment.is_electronic:
            context['count_waiting_for_deliveries'] = groups.filter_waiting_for_deliveries().count()
        context['count_corrected'] = groups.filter_by_status('corrected').count()

        paginator = self._get_paginator(groups)
        page = self.request.GET.get('page')

        context['groups'] = get_paginated_page(paginator, page)
        context['allgroups'] = groups
        context['currentpage'] = self.currentpage

        context['orderingform'] = self.orderingform
        context['order_by'] = self.order_by

        context['examinermode'] = 'normal' # The mode is normal for all non supported grade plugins
        if assignment.grading_system_plugin_id == 'devilry_gradingsystemplugin_approved':
            context['examinermode_form'] = self.examinermode_form
            context['examinermode'] = self.examinermode

        return context

    def get_queryset(self):
        return Assignment.objects.filter_examiner_has_access(self.request.user)

    def _get_quickfeedback_formcollection(self):
        return QuickFeedbackFormCollection(
            request=self.request,
            assignment=self.get_object(),
            groupqueryset=self._get_groupqueryset())

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        quickfeedback_formcollection = self._get_quickfeedback_formcollection()
        if quickfeedback_formcollection.is_valid():
            quickfeedback_formcollection.save()
            return HttpResponseRedirect(self.get_success_url())
        else:
            context = self.get_context_data(quickfeedback_formcollection=quickfeedback_formcollection)
            return self.render_to_response(context=context)


class WaitingForFeedbackOverview(AllGroupsOverview):
    template_name = "devilry_examiner/waiting-for-feedback-list.django.html"
    currentpage = 'waiting_for_feedback'

    def get_context_data(self, **kwargs):
        context = super(WaitingForFeedbackOverview, self).get_context_data(**kwargs)

        groups = context['allgroups']
        groups = groups.filter_waiting_for_feedback()

        page = self.request.GET.get('page')

        context['groups'] = get_paginated_page(self._get_paginator(groups), page)

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

        context['groups'] = get_paginated_page(self._get_paginator(groups), page)

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

        context['groups'] = get_paginated_page(self._get_paginator(groups), page)

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
