from __future__ import unicode_literals

import math
import random

from django import forms
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy
from django.views.generic import TemplateView
from django_cradmin import crapp

from devilry.apps.core.models import Examiner, RelatedExaminer
from devilry.devilry_admin.views.assignment.students import groupview_base
from devilry.devilry_cradmin import devilry_listbuilder


class SelectMethodView(TemplateView):
    template_name = 'devilry_admin/assignment/examiners/bulk_organize/select_method.django.html'


class RandomOrganizeForm(groupview_base.SelectedGroupsForm):
    selected_relatedexaminers = forms.ModelMultipleChoiceField(
        queryset=RelatedExaminer.objects.none()
    )

    def __init__(self, *args, **kwargs):
        selectable_relatedexaminers_queryset = kwargs.pop('selectable_relatedexaminers_queryset')
        super(RandomOrganizeForm, self).__init__(*args, **kwargs)
        self.fields['selected_relatedexaminers'].queryset = selectable_relatedexaminers_queryset


class RandomOrganizeTargetRenderer(devilry_listbuilder.assignmentgroup.GroupTargetRenderer):
    def get_submit_button_text(self):
        return ugettext_lazy('Randomly assign selected students to selected examiners')


class RandomView(groupview_base.BaseMultiselectView):
    filterview_name = 'random'
    template_name = 'devilry_admin/assignment/examiners/bulk_organize/random.django.html'

    def get_target_renderer_class(self):
        return RandomOrganizeTargetRenderer

    def get_form_class(self):
        return RandomOrganizeForm

    def __get_relatedexaminerqueryset(self):
        assignment = self.request.cradmin_role
        period = assignment.period
        queryset = RelatedExaminer.objects\
            .filter(period=period)\
            .select_related('user')\
            .exclude(active=False)
        return queryset

    def get_form_kwargs(self):
        kwargs = super(RandomView, self).get_form_kwargs()
        kwargs['selectable_relatedexaminers_queryset'] = self.__get_relatedexaminerqueryset()
        return kwargs

    # def get_success_message(self, candidatecount):
    #     return ugettext_lazy('Removed %(count)s students from this assignment.') % {
    #         'count': candidatecount
    #     }

    def get_success_url(self):
        return self.request.cradmin_instance.reverse_url(
            appname='examineroverview',
            viewname=crapp.INDEXVIEW_NAME)

    def __clear_examiners(self, groupqueryset):
        Examiner.objects.filter(assignmentgroup__in=groupqueryset).delete()

    def __random_organize_examiners(self, groupqueryset, relatedexaminerqueryset):
        relatedexaminers = list(relatedexaminerqueryset)
        groups = list(groupqueryset)
        max_per_examiner = int(math.ceil(len(groups) / len(relatedexaminers)))
        relatedexaminer_to_count_map = {}
        examiners_to_create = []
        for group in groupqueryset:
            relatedexaminer = random.choice(relatedexaminers)
            if relatedexaminer.id not in relatedexaminer_to_count_map:
                relatedexaminer_to_count_map[relatedexaminer.id] = 0
            relatedexaminer_to_count_map[relatedexaminer.id] += 1
            if relatedexaminer_to_count_map[relatedexaminer.id] > max_per_examiner:
                relatedexaminers.remove(relatedexaminer)
            examiner_to_create = Examiner(relatedexaminer=relatedexaminer, assignmentgroup=group)
            examiners_to_create.append(examiner_to_create)
        Examiner.objects.bulk_create(examiners_to_create)

    def form_valid(self, form):
        groupqueryset = form.cleaned_data['selected_items']
        relatedexaminerqueryset = form.cleaned_data['selected_relatedexaminers']
        self.__clear_examiners(groupqueryset=groupqueryset)
        self.__random_organize_examiners(groupqueryset=groupqueryset,
                                         relatedexaminerqueryset=relatedexaminerqueryset)
        # messages.success(self.request, self.get_success_message(candidatecount=candidatecount))
        return redirect(self.get_success_url())


class App(crapp.App):
    appurls = [
        crapp.Url(r'^$',
                  SelectMethodView.as_view(),
                  name=crapp.INDEXVIEW_NAME),
        crapp.Url(r'^random/(?P<filters_string>.+)?$',
                  RandomView.as_view(),
                  name='random'),
    ]
