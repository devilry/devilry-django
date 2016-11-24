# # -*- coding: utf-8 -*-
from __future__ import unicode_literals

# 3rd party imports
from crispy_forms import layout

# Django imports
from django import forms
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.db import models

# CrAdmin imports
from django_cradmin.crispylayouts import PrimarySubmit, DefaultSubmit, CollapsedSectionLayout
from django_cradmin.viewhelpers import formbase
from django_cradmin.viewhelpers import update

# Devilry imports
from devilry.devilry_qualifiesforexam import models as status_models
from devilry.apps.core import models as core_models


class QualificationForm(forms.Form):
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

    def get_buttons(self):
        buttons = super(AbstractQualificationPreviewView, self).get_buttons()
        buttons.append(DefaultSubmit('back', _('Back')))
        return buttons

    def get_button_layout(self):
        return [
            layout.Div(*self.get_buttons(), css_class='devilry-dashboard-container')
        ]

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
        return core_models.RelatedStudent.objects.filter(period=period)\
            .select_related('user')\
            .order_by('user__fullname')

    def form_valid(self, form):
        return HttpResponseRedirect(self.request.cradmin_app.reverse_appindexurl())


class QualificationPreviewView(AbstractQualificationPreviewView):
    """
    View that lists the current qualification status for students.

    This view lists all the students on the course for this period.
    """
    template_name = 'devilry_qualifiesforexam/preview.django.html'
    form_class = QualificationForm

    def dispatch(self, request, *args, **kwargs):
        """
        Check if a :class:`~.devilry_qualifiesforexam.models.Status` with ``status`` set to
        ``ready`` exists for the period. If it exists, redirect to the final export view.

        Args:
            request: ``HttpRequest`` with the attached cradmin_role.
        """
        status = status_models.Status.objects.order_by('-createtime').first()
        if status:
            if status.status == status_models.Status.READY:
                return HttpResponseRedirect(self.request.cradmin_app.reverse_appurl(
                    viewname='show-status',
                    kwargs={
                        'roleid': self.request.cradmin_role.id
                    }
                ))
        if 'plugintypeid' not in request.session or 'passing_relatedstudentids' not in request.session:
            return HttpResponseRedirect(self.request.cradmin_app.reverse_appindexurl())
        return super(QualificationPreviewView, self).dispatch(request, *args, **kwargs)

    def get_buttons(self):
        buttons = super(QualificationPreviewView, self).get_buttons()
        buttons.append(PrimarySubmit('save', _('Save')))
        return buttons

    def get_context_data(self, **kwargs):
        context_data = super(QualificationPreviewView, self).get_context_data()
        context_data['period'] = self.request.cradmin_role
        context_data['plugintypeid'] = self.request.session['plugintypeid']
        context_data['relatedstudents'] = self.get_relatedstudents_queryset(self.request.cradmin_role)
        context_data['passing_relatedstudentids'] = set(self.request.session['passing_relatedstudentids'])

        return context_data

    def _create_status(self, plugintypeid):
        """
        Creates and saves a entry in the database for current examqualification-status for students.

        Returns:
            A :obj:`~.devilry.devilry_qualifiesforexam.models.Status` instance.
        """
        status = status_models.Status.objects.create(
                status=status_models.Status.READY,
                period=self.request.cradmin_role,
                user=self.request.user,
                plugin=plugintypeid
        )
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
        # Get passing_relatedstudentids and plugintypeid and delete from session
        passing_relatedstudentids = set(self.request.session['passing_relatedstudentids'])
        plugintypeid = self.request.session['plugintypeid']
        del self.request.session['passing_relatedstudentids']
        del self.request.session['plugintypeid']

        if 'save' in self.request.POST:
            status = self._create_status(plugintypeid)
            self._bulk_create_relatedstudents(status, passing_relatedstudentids)
            return HttpResponseRedirect(self.request.cradmin_app.reverse_appurl(
                viewname='show-status',
                kwargs={
                    'roleid': self.request.cradmin_role.id,
                    'statusid': status.id
                }
            ))
        return super(QualificationPreviewView, self).form_valid(form)


class QualificationStatusForm(forms.Form):
    pass


class QualificationStatusView(AbstractQualificationPreviewView):
    """
    View for showing the current :class:`~.devilry.devilry_qualifiesforexam.models.Status` of the
    qualifications list.
    """
    template_name = 'devilry_qualifiesforexam/show_status.html'
    form_class = QualificationStatusForm

    def dispatch(self, request, *args, **kwargs):
        self.status = status_models.Status.objects.get(id=kwargs.get('statusid'))
        return super(QualificationStatusView, self).dispatch(request, *args, **kwargs)

    def get_buttons(self):
        buttons = super(QualificationStatusView, self).get_buttons()
        if self.status.status == status_models.Status.READY:
            buttons.append(PrimarySubmit('retract', _('Retract'), css_class='btn btn-primary'))
        return buttons

    def get_button_layout(self):
        return [
            layout.Div(*self.get_buttons(), css_class='devilry-dashboard-container')
        ]

    def _get_qualifiesforexam_queryset(self):
        """
        Join `~.devilry.apps.core.models.User` with
        `~.devilry.deviry_qualifiesforexam.models.QualifiesForFinalExam`

        Returns:
            queryset: of `~.devilry.deviry_qualifiesforexam.models.QualifiesForFinalExam`.
        """
        return status_models.QualifiesForFinalExam.objects\
            .select_related('relatedstudent__user')

    def _get_status(self):
        """
        Join tables for `~.devilry.deviry_qualifiesforexam.models.Status` such as
        qualification results for the ``RelatedStudent``s on the period and their related user
        which info will be used in the view.

        Returns:
            status: `~.devilry.deviry_qualifiesforexam.models.Status`.
        """
        status = status_models.Status.objects\
            .select_related('period')\
            .prefetch_related(
                models.Prefetch(
                    'students',
                    queryset=self._get_qualifiesforexam_queryset()))\
            .get(id=self.status.id)
        return status

    def get_context_data(self, **kwargs):
        context_data = super(QualificationStatusView, self).get_context_data(**kwargs)
        current_status = self._get_status()
        context_data['status'] = current_status

        # Add RelatedStudents to list and the IDs of the relatedstudents that qualify.
        qualifiesforexam = list(current_status.students.all())
        qualifying_studentids = [q.relatedstudent.id for q in qualifiesforexam if q.qualifies]
        relatedstudents = self.get_relatedstudents_queryset(self.request.cradmin_role)
        context_data['passing_relatedstudentids'] = qualifying_studentids
        context_data['num_students_qualify'] = len(qualifying_studentids)
        context_data['relatedstudents'] = relatedstudents
        context_data['num_students'] = len(relatedstudents)
        return context_data

    def form_valid(self, form):
        if 'retract' in self.request.POST:
            return HttpResponseRedirect(self.request.cradmin_app.reverse_appurl(
                viewname='retract-status',
                kwargs={
                    'statusid': self.status.id
                }
            ))
        return super(QualificationStatusView, self).form_valid(form)


class RetractStatusForm(forms.ModelForm):
    """
    Form for providing a retracted-message for the status
    """
    class Meta:
        fields = ['message']
        model = status_models.Status
        help_texts = {
            'message': 'Provide a message as to why the Status needs to be retracted.'
        }

    @classmethod
    def get_field_layout(cls):
        return ['message']


class StatusRetractView(update.UpdateView):
    """
    Simple model-update view.

    This view is for providing a message of why the status was retracted.
    """
    model = status_models.Status

    def get_pagetitle(self):
        return 'Why is the status retracted?'

    def get_form_class(self):
        return RetractStatusForm

    def get_field_layout(self):
        field_layout = []
        field_layout.extend(self.get_form_class().get_field_layout())
        return field_layout

    def get_queryset_for_role(self, role):
        role_name = self.request.cradmin_instance.is_admin()
        if not role_name:
            raise PermissionDenied
        return role.qualifiedforexams_status

    def get_object(self, queryset=None):
        return status_models.Status.objects.get(
                id=self.kwargs.get('statusid'),
                period=self.request.cradmin_role
        )

    def save_object(self, form, commit=True):
        status = super(StatusRetractView, self).save_object(form=form, commit=False)
        status.status = status_models.Status.NOTREADY
        status.plugin = None
        status = super(StatusRetractView, self).save_object(form=form, commit=commit)
        return status

    def get_success_url(self):
        if self.get_submit_save_and_continue_edititing_button_name() in self.request.POST:
            return self.request.cradmin_app.reverse_appurl(

            )
        return self.request.cradmin_app.reverse_appindexurl()

    def get_form_invalid_message(self, form):
        return 'Cannot retract status without a message.'
