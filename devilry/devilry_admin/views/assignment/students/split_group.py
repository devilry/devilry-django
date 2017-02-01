from __future__ import unicode_literals

from crispy_forms import layout
from django.views.generic.detail import SingleObjectMixin
from django_cradmin.crispylayouts import PrimarySubmit
from django_cradmin.viewhelpers import formbase
from django import forms
from django.http import Http404
from django_cradmin import crapp, crinstance
from django.utils.translation import ugettext_lazy
from django_cradmin.viewhelpers.mixins import QuerysetForRoleMixin
from django_cradmin.widgets.selectwidgets import WrappedSelect
from django.contrib import messages

from devilry.apps.core.models import AssignmentGroup, Candidate
from devilry.apps.core.models.assignment_group import GroupPopNotCandiateError, GroupPopToFewCandiatesError


class SplitGroupForm(forms.Form):
    candidates = forms.ModelChoiceField(
        widget=WrappedSelect(),
        queryset=Candidate.objects.none()
    )

    def __init__(self, *args, **kwargs):
        candidate_queryset = kwargs.pop('candidate_queryset')
        super(SplitGroupForm, self).__init__(*args, **kwargs)
        self.fields['candidates'].queryset = candidate_queryset
        self.fields['candidates'].label_from_instance = self.label_from_instance

    @staticmethod
    def label_from_instance(obj):
        return obj.relatedstudent.user.get_displayname()


class SplitGroupView(QuerysetForRoleMixin, SingleObjectMixin, formbase.FormView):
    form_class = SplitGroupForm
    template_name = 'devilry_admin/assignment/students/split_groups.django.html'

    def dispatch(self, request, *args, **kwargs):
        self.group = self.get_object()
        self.object = self.get_object()
        self.assignment = self.request.cradmin_role
        self.devilryrole = self.request.cradmin_instance.get_devilryrole_for_requestuser()
        if self.assignment.is_fully_anonymous and self.devilryrole != 'departmentadmin':
            raise Http404()
        return super(SplitGroupView, self).dispatch(request, *args, **kwargs)

    def get_pagetitle(self):
        return ugettext_lazy('Split students from project group')

    def __get_candidate_queryset(self):
        return self.group.candidates.select_related('relatedstudent__user')

    def get_button_layout(self):
        return [
            PrimarySubmit('split', ugettext_lazy('Split'))
        ]

    def get_queryset_for_role(self, role):
        return AssignmentGroup.objects.filter(parentnode=role).select_related('parentnode')

    def form_valid(self, form):
        return super(SplitGroupView, self).form_valid(form)

    def get_field_layout(self):
        return [
            layout.Div('candidates', css_class='')
        ]

    def form_valid(self, form):
        candidate = form.cleaned_data['candidates']
        try:
            self.group.pop_candidate(candidate)
        except GroupPopNotCandiateError as e:
            messages.warning(
                self.request,
                str(e)
            )
        except GroupPopToFewCandiatesError as e:
            messages.warning(
                self.request,
                str(e)
            )
        else:
            messages.success(
                self.request,
                ugettext_lazy('{} was removed from the project group'
                              .format(candidate.relatedstudent.user.get_displayname()))
            )
        return super(SplitGroupView, self).form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(SplitGroupView, self).get_form_kwargs()
        kwargs['candidate_queryset'] = self.__get_candidate_queryset()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(SplitGroupView, self).get_context_data(**kwargs)
        context['group'] = self.group
        return context

    def get_success_url(self):
        return self.request.cradmin_app.reverse_appindexurl(kwargs={'pk': self.group.id})


class App(crapp.App):
    appurls = [
        crapp.Url(r'^(?P<pk>\d+)$', SplitGroupView.as_view(), name=crapp.INDEXVIEW_NAME),
    ]
