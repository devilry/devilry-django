# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Django imports
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django import forms

# CrAdmin imports
from django_cradmin.crispylayouts import PrimarySubmit, DefaultSubmit
from django_cradmin.viewhelpers import formbase

# Devilry imports
from devilry.devilry_qualifiesforexam import models as status_models
from devilry.apps.core import models as core_models


class MyForm(forms.Form):
    pass


class AbstractQualificationPreviewView(formbase.FormView):
    """
    Abstract superclass for preview views
    """

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


class QualificationPreviewView(AbstractQualificationPreviewView):
    """
    View that lists the current qualification status for students.

    This view lists all the students on the course for this period.
    """
    template_name = 'devilry_qualifiesforexam/preview.django.html'
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
        context_data['qualifying_assignmentids'] = set(self.request.session['qualifying_assignmentids'])
        context_data['passing_relatedstudentids'] = set(self.request.session['passing_relatedstudentids'])

        return context_data

    def _create_status(self, plugintypeid):
        """
        Creates and saves a entry in the database for current examqualification-status for students.

        Returns:
            A :obj:`~.devilry.devilry_qualifiesforexam.models.Status` instance saved to the db.
        """
        status = status_models.Status.objects.create(
                status=status_models.Status.READY,
                period=self.request.cradmin_role,
                user=self.request.user,
                plugin=plugintypeid
        )
        status.full_clean()
        return status

    def _bulk_create_relatedstudents(self, status, passing_relatedstudentids):
        """
        Bulk create :obj:`~.devilry.devilry_qualifiesforexam.models.QualifiesForFinalExam` entries in the database
        for each student. Each entry has a ForeignKey to ``status``.

        Args:
            status: ForeignKey reference for each
                :obj:`~.devilry.devilry_qualifiesforexam.models.QualifiesForFinalExam`.
        """
        qualifies_for_final_exam_objects = []
        for relatedstudent in self.get_relatedstudents_queryset(self.request.cradmin_role):
            qualifies_for_final_exam_objects.append(status_models.QualifiesForFinalExam(
                relatedstudent=relatedstudent,
                status=status,
                qualifies=True if relatedstudent.id in passing_relatedstudentids else False
            ))
        status_models.QualifiesForFinalExam.objects.bulk_create(qualifies_for_final_exam_objects)

    def form_valid(self, form):
        passing_relatedstudentids = set(self.request.session['passing_relatedstudentids'])
        plugintypeid = self.request.session['plugintypeid']

        if 'save' in self.request.POST:
            status = self._create_status(plugintypeid)
            self._bulk_create_relatedstudents(status, passing_relatedstudentids)
            return HttpResponseRedirect(self.request.cradmin_app.reverse_appurl(
                viewname='show-status',
                kwargs={
                    'roleid': self.request.cradmin_role.id
                }
            ))
        elif 'back' in self.request.POST:
            return HttpResponseRedirect(self.request.cradmin_app.reverse_appurl(
                viewname='configure-plugin',
                kwargs={
                    'roleid': self.request.cradmin_role.id,
                    'plugintypeid': plugintypeid
                }
            ))


class QualificationStatusPreview(AbstractQualificationPreviewView):
    """
    View for showing the current :class:`~.devilry.devilry_qualifiesforexam.models.Status` of the
    qualifications list.
    """
    template_name = 'devilry_qualifiesforexam/show_status.html'
    form_class = MyForm

    def _get_qualifiesforexam_queryset(self):
        """
        """
        return status_models.QualifiesForFinalExam.objects\
            .select_related('relatedstudent')\
            .order_by('relatedstudent__user__fullname',
                      'relatedstudent__user__shortname')

    def get_queryset_for_role(self):
        """
        Prefetches whats need for to print the
        """
        return status_models.Status.objects\
            .select_related('period')\
            .prefetch_related(
                models.Prefetch(
                        'students',
                        queryset=self._get_qualifiesforexam_queryset()))

    def _get_qualifyingstudentids(self, qualifiesforexam):
        """
        """
        qualifyingids = []
        for qualifying_student in qualifiesforexam:
            if qualifying_student.qualifies:
                qualifyingids.append(qualifying_student.relatedstudent.id)
        return qualifyingids

    def _get_relatedstudents(self, period):
        """
        Get all RelatedStudents for Period.
        """
        return core_models.RelatedStudent.objects.filter(period=period)

    def get_context_data(self, **kwargs):
        context_data = super(QualificationStatusPreview, self).get_context_data(**kwargs)

        current_status = self.get_queryset_for_role()[0].get_current_status(self.request.cradmin_role)
        context_data['saved_by'] = current_status.user
        context_data['period'] = current_status.period

        context_data['saved_date'] = current_status.createtime
        context_data['status'] = current_status.status

        qualifiesforexam = current_status.students.all()
        qualifying_studentids = [q.relatedstudent.id for q in qualifiesforexam if q.qualifies]
        relatedstudents = self._get_relatedstudents(self.request.cradmin_role)
        context_data['passing_relatedstudentids'] = qualifying_studentids
        context_data['num_students_qualify'] = len(qualifying_studentids)
        context_data['relatedstudents'] = relatedstudents
        context_data['num_students'] = len(relatedstudents)
        return context_data
