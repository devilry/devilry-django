from datetime import datetime
from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import Http404
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.views.generic import ListView

from devilry.apps.core.models import Assignment
from devilry.devilry_detektor.models import DetektorAssignment
from devilry.devilry_detektor.tasks import run_detektor_on_assignment
from devilry.devilry_detektor.tasks import FileMetasByFiletype
from devilry.devilry_detektor.models import CompareTwoCacheItem


class AssignmentAssemblyViewGetForm(forms.Form):
    language = forms.ChoiceField(
        required=False,
        choices=[(language, language) for language in FileMetasByFiletype.SUPPORTED_FILE_TYPES])


class AssignmentAssemblyView(ListView):
    model = CompareTwoCacheItem
    pk_url_kwarg = 'assignmentid'
    context_object_name = 'comparetwo_cacheitems'
    template_name = 'devilry_detektor/admin/assignmentassembly.django.html'
    paginate_by = 100

    def dispatch(self, request, *args, **kwargs):
        self.request = request
        self.assignmentid = kwargs['assignmentid']
        self.cachelanguages = list(self._get_detektorassignment().cachelanguages.all())
        form = AssignmentAssemblyViewGetForm(request.GET)
        if form.is_valid():
            self.language = form.cleaned_data['language']
            if not self.language and self.cachelanguages:
                self.language = self.cachelanguages[0].language
        else:
            return HttpResponseBadRequest(form.errors.as_text())
        return super(AssignmentAssemblyView, self).dispatch(request, *args, **kwargs)

    def _get_assignment_queryset(self):
        return Assignment.objects.filter_admin_has_access(self.request.user)\
            .select_related(
                'parentnode',  # Period
                'parentnode__parentnode')  # Subject

    def _get_assignment(self, *args, **kwargs):
        if not hasattr(self, '_assignment'):
            self._assignment = get_object_or_404(self._get_assignment_queryset(),
                                                 id=self.assignmentid)
        return self._assignment

    def _get_detektorassignment(self):
        if not hasattr(self, '_detektorassignment'):
            self._detektorassignment, created = DetektorAssignment.objects.get_or_create(
                assignment_id=self._get_assignment().id)
        return self._detektorassignment

    def get_success_url(self):
        return reverse('devilry_detektor_admin_assignmentassembly',
                       kwargs={'assignmentid': self.assignmentid})

    def post(self, *args, **kwargs):
        detektorassignment = self._get_detektorassignment()
        if detektorassignment.status != 'running':
            detektorassignment.processing_started_datetime = datetime.now()
            detektorassignment.processing_started_by_id = self.request.user
            detektorassignment.status = 'running'
            detektorassignment.save()
            run_detektor_on_assignment.delay(assignment_id=self._get_assignment().id)
        # NOTE: We ignore when the task is already running - this only occurs
        # when two admins click the button at the same time, and the message
        # shown is good enough for such an unlikely case.

        return HttpResponseRedirect(self.get_success_url())

    def get_queryset(self):
        if self.language:
            return super(AssignmentAssemblyView, self).get_queryset()\
                .order_by('-scaled_points')\
                .filter(
                    language__detektorassignment=self._get_detektorassignment(),
                    language__language=self.language)\
                .select_related(
                    'parseresult1',
                    'parseresult1__delivery',
                    'parseresult1__delivery__deadline',
                    'parseresult1__delivery__deadline__assignment_group',
                    'parseresult1__delivery__deadline__assignment_group__parentnode',  # Assignment
                    'parseresult1__delivery__deadline__assignment_group__parentnode__parentnode',  # Period
                    'parseresult1__delivery__deadline__assignment_group__parentnode__parentnode__parentnode',  # Subject
                    'parseresult2',
                    'parseresult2__delivery',
                    'parseresult2__delivery__deadline',
                    'parseresult2__delivery__deadline__assignment_group',
                    'parseresult2__delivery__deadline__assignment_group__parentnode',  # Assignment
                    'parseresult2__delivery__deadline__assignment_group__parentnode__parentnode',  # Period
                    'parseresult2__delivery__deadline__assignment_group__parentnode__parentnode__parentnode'  # Subject
                )\
                .prefetch_related(
                    'parseresult1__delivery__deadline__assignment_group__candidates',
                    'parseresult1__delivery__deadline__assignment_group__candidates__student',
                    'parseresult1__delivery__deadline__assignment_group__candidates__student__devilryuserprofile',
                    'parseresult2__delivery__deadline__assignment_group__candidates',
                    'parseresult2__delivery__deadline__assignment_group__candidates__student',
                    'parseresult2__delivery__deadline__assignment_group__candidates__student__devilryuserprofile')
        else:
            return super(AssignmentAssemblyView, self).get_queryset().none()

    def get_context_data(self, **kwargs):
        context = super(AssignmentAssemblyView, self).get_context_data(**kwargs)
        context['detektorassignment'] = self._get_detektorassignment()
        context['cachelanguages'] = self.cachelanguages
        context['active_language'] = self.language
        context['assignment'] = self._get_assignment()
        if hasattr(settings, 'DEVILRY_DETEKTOR_DISABLED'):
            context['detektor_disabled'] = getattr(settings, 'DEVILRY_DETEKTOR_DISABLED')
        return context
