# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Django imports
from crispy_forms import layout
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django import forms

# 3rd party
from django_cradmin.crispylayouts import PrimarySubmit, DefaultSubmit

# CrAdmin imports
from django_cradmin.viewhelpers import formbase

# Devilry imports
from devilry.apps.core import models as core_models
from devilry.devilry_qualifiesforexam import models as status_models


class MyForm(forms.Form):
    pass


class AbstractQualificationPreviewView(formbase.FormView):
    """
    Abstract superclass for preview views
    """
    template_name = 'devilry_qualifiesforexam/preview.django.html'

    @classmethod
    def deserialize_preview(cls, serialized):
        pass

    def serialize_preview(self, form):
        pass

    def get_field_layout(self):
        return []

    def get_relatedstudents_queryset(self, period):
        """
        Get all the :class:`~.devilry.apps.core.models.RelatedStudent`s for ``period``.

        Args:
            period: The period to fetch ``RelatedStudent``s for.

        Returns:
            QuerySet: QuerySet for :class:`~.devilry.apps.core.models.RelatedStudent`
        """
        return core_models.RelatedStudent.objects.filter(period=period)

    def get(self, request, *args, **kwargs):
        """
        Override ``get()`` to temporarily store the session data on the instance.s
        """
        # Store session data on instance, and delete from session.
        self.qualifying_assignmentids = set(request.session['qualifying_assignmentids'])
        self.passing_relatedstudentids = set(request.session['passing_relatedstudentids'])
        del self.request.session['qualifying_assignmentids']
        del self.request.session['passing_relatedstudentids']
        return super(AbstractQualificationPreviewView, self).get(request, *args, **kwargs)


class QualificationPreviewView(AbstractQualificationPreviewView):
    """
    View that lists the current qualification status for students.

    This view lists all the students on the course for this period.
    """
    form_class = MyForm

    def get_buttons(self):
        return [
            DefaultSubmit('back', _('Back')),
            PrimarySubmit('save', _('Save'))
        ]

    def get_context_data(self, **kwargs):
        context_data = super(QualificationPreviewView, self).get_context_data()

        context_data['period'] = self.request.cradmin_role
        context_data['relatedstudents'] = self.get_relatedstudents_queryset(self.request.cradmin_role)
        context_data['qualifying_assignmentids'] = self.qualifying_assignmentids
        context_data['passing_relatedstudentids'] = self.passing_relatedstudentids

        return context_data

    def _create_status(self):
        """
        Creates and saves a entry in the database for current examqualification-status for students.

        Returns:
            A :obj:`~.devilry.devilry_qualifiesforexam.models.Status` instance saved to the db.
        """
        return status_models.Status.objects.create(
            status=status_models.Status.NOTREADY,
            period=self.request.cradmin_role,
            user=self.request.requestuser,
            plugin='approvedplugin',
        )

    def _bulk_create_relatedstudents(self, status):
        """
        Bulk create :obj:`~.devilry.devilry_qualifiesforexam.models.QualifiesForFinalExam` entries in the database
        for each student. Each entry has a ForeignKey to ``status``.

        Args:
            status: ForeignKey reference for each
                :obj:`~.devilry.devilry_qualifiesforexam.models.QualifiesForFinalExam`.
        """
        qualifies_for_final_exam_objects = []
        for relatedstudent in self.get_relatedstudents_queryset():
            qualifies_for_final_exam_objects.append(status_models.QualifiesForFinalExam(
                relatedstudent=relatedstudent,
                status=status,
                qualifies=True if relatedstudent.id in self.passing_relatedstudentids else False
            ))
        status_models.QualifiesForFinalExam.objects.bulk_create(qualifies_for_final_exam_objects)

    def form_valid(self, form):
        # ... do something with the form ..
        if 'save' in self.request.POST:
            status = self._create_status()
            self._bulk_create_relatedstudents(status=status)
            return HttpResponseRedirect(self.request.cradmin_app.reverse_appurl('preview'))
        elif 'back' in self.request.POST:
            print 'Back invoked, return to previous plugin view.'
