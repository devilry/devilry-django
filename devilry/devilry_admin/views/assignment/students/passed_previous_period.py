from __future__ import unicode_literals

from crispy_forms import layout
from django import forms
from django_cradmin import crapp
from django.db import models
from django.contrib import messages
from django.shortcuts import redirect
from django_cradmin.viewhelpers import formbase
from django.views.generic.detail import SingleObjectMixin
from django_cradmin.crispylayouts import PrimarySubmit
from django.utils.translation import ugettext_lazy
from django_cradmin.viewhelpers import listbuilderview
from devilry.apps.core.models import Assignment
from django_cradmin.viewhelpers.mixins import QuerysetForRoleMixin
from django_cradmin.widgets.selectwidgets import WrappedSelect
from django_cradmin.widgets.modelchoice import ModelChoiceWidget
from django.http import Http404


from devilry.apps.core.models import Period


class SelectPeriodForm(forms.Form):
    semester = forms.ModelChoiceField(
        widget=forms.RadioSelect(),
        queryset=Period.objects.none()
    )

    def __init__(self, *args, **kwargs):
        period_queryset = kwargs.pop('period_queryset')
        super(SelectPeriodForm, self).__init__(*args, **kwargs)
        self.fields['semester'].queryset = period_queryset
        self.fields['semester'].label_from_instance = self.label_from_instance

    @staticmethod
    def label_from_instance(obj):
        return "{} - {}".format(obj.short_name, obj.long_name)


class SelectPeriodView(formbase.FormView):
    form_class = SelectPeriodForm
    template_name = 'devilry_admin/assignment/students/passed_previous_period/select-period-view.django.html'

    def dispatch(self, request, *args, **kwargs):
        self.assignment = self.request.cradmin_role
        self.devilryrole = self.request.cradmin_instance.get_devilryrole_for_requestuser()
        if self.assignment.is_fully_anonymous and self.devilryrole != 'departmentadmin':
            raise Http404()
        if self.assignment.is_semi_anonymous and self.devilryrole == 'periodadmin':
            raise Http404()
        return super(SelectPeriodView, self).dispatch(request, *args, **kwargs)

    def get_pagetitle(self):
        return ugettext_lazy('Select the earliest semester you want to approve for')

    def __get_period_queryset(self):
        return Period.objects.filter(
            parentnode=self.assignment.parentnode.parentnode,
            assignments__short_name=self.assignment.short_name
        ).prefetch_related('assignments')\
            .exclude(start_time__gte=self.assignment.parentnode.start_time)\
            .order_by('start_time')

    def get_button_layout(self):
        return [
            PrimarySubmit('Next', ugettext_lazy('Next'))
        ]

    def get_field_layout(self):
        return [
            layout.Div('semester', css_class='')
        ]

    def form_valid(self, form):
        period = form.cleaned_data['semester']
        return redirect(self.get_redirect_url(period))

    def get_form_kwargs(self):
        kwargs = super(SelectPeriodView, self).get_form_kwargs()
        kwargs['period_queryset'] = self.__get_period_queryset()
        return kwargs
    
    def get_context_data(self, **kwargs):
        return super(SelectPeriodView, self).get_context_data(**kwargs)

    def get_redirect_url(self, period):
        return self.request.cradmin_app.reverse_appurl(
            'assignments',
            kwargs={'pk': period.id}
        )


class PassedPreviousAssignmentView(SingleObjectMixin, listbuilderview.View):
    model = Assignment
    template_name = 'devilry_admin/assignment/students/passed_previous_period/assignment-overview.django.html'

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.period = self.get_object()
        self.assignment = self.request.cradmin_role
        self.devilryrole = self.request.cradmin_instance.get_devilryrole_for_requestuser()
        if self.assignment.is_fully_anonymous and self.devilryrole != 'departmentadmin':
            raise Http404()
        if self.assignment.is_semi_anonymous and self.devilryrole == 'periodadmin':
            raise Http404()
        return super(PassedPreviousAssignmentView, self).dispatch(request, *args, **kwargs)

    def get_queryset_for_role(self, role):
        return Period.objects.filter(assignments__short_name=role.short_name)\
            .prefetch_related('assignments')

    def get_pagetitle(self):
        return ugettext_lazy('Confirm assignmnets')




class App(crapp.App):
    appurls = [
        crapp.Url(r'^$', SelectPeriodView.as_view(), name=crapp.INDEXVIEW_NAME),
        crapp.Url(r'^assignment/(?P<pk>\d+)$', PassedPreviousAssignmentView.as_view(), name='assignments')
    ]
