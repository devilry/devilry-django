# -*- coding: utf-8 -*-
import json

# Django imports
from django import forms
from django.utils.translation import gettext_lazy
from django.views import generic
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.db import models
from django.db.models import F
from django.db.models.functions import NullIf
from django.db.models import Value

# CrAdmin imports
from cradmin_legacy.crispylayouts import PrimarySubmit
from cradmin_legacy.viewhelpers import update

# Devilry imports
from devilry.devilry_qualifiesforexam import models as status_models
from devilry.apps.core import models as core_models
from devilry.devilry_qualifiesforexam.tablebuilder import tablebuilder
from devilry.devilry_qualifiesforexam.listbuilder.assignment_listbuilder_list import AssignmentListBuilderList


class AbstractQualificationPreviewView(generic.FormView):
    """
    Abstract superclass for preview views
    """
    form_class = forms.Form

    def get_order_by_queryparam(self):
        return self.request.GET.get('order_by', '')

    def get_order_by(self):
        order_by = self.get_order_by_queryparam()
        if order_by == 'fullname':
            return 'user__fullname'
        if order_by == 'username':
            return 'user__shortname'
        return 'user__lastname'

    def get_relatedstudents_queryset(self, period):
        """
        Get all the :class:`~.devilry.apps.core.models.RelatedStudent`s for ``period``.

        Args:
            period: The period to fetch ``RelatedStudent``s for.

        Returns:
            QuerySet: QuerySet for :class:`~.devilry.apps.core.models.RelatedStudent`
        """
        order_by = self.get_order_by()
        queryset = core_models.RelatedStudent.objects.filter(period=period) \
            .select_related('user')\
            .order_by(order_by, 'user__shortname')
        return queryset

    def _get_tablebuilder(self, relatedstudents, qualifying_studentids):
        """
        Creates a :obj:`~.devilry.devilry_qualifiesforexam.tablebuilder.tablebuilder.QualifiesTableBuilderTable`.

        Args:
            relatedstudents: All relatedstudents for a period.
            qualifying_studentids: relatedstudent IDs for students that are qualified to take the final exam.

        Returns:
            :obj:`~.devilry.devilry_qualifiesforexam.tablebuilder.tablebuilder.QualifiesTableBuilderTable` instance.
        """
        rows = []
        for relatedstudent in relatedstudents:
            row_items = [relatedstudent, 'yes' if relatedstudent.id in qualifying_studentids else 'no']
            rows.append(row_items)
        builder = tablebuilder.QualifiesTableBuilderTable.from_qualifying_items(row_items_list=rows)
        return builder

    def form_valid(self, form):
        return HttpResponseRedirect(str(self.request.cradmin_app.reverse_appindexurl()))


class QualificationPreviewView(AbstractQualificationPreviewView):
    """
    View that lists the current qualification status for students.

    This view lists all the students on the course for this period.
    """
    template_name = 'devilry_qualifiesforexam/status_preview.django.html'

    def dispatch(self, request, *args, **kwargs):
        """
        Check if a :class:`~.devilry_qualifiesforexam.models.Status` with ``status`` set to
        ``ready`` exists for the period. If it exists, redirect to the final export view.

        Args:
            request: ``HttpRequest`` with the attached cradmin_role.
        """
        if 'plugintypeid' not in request.session or 'passing_relatedstudentids' not in request.session:
            return HttpResponseRedirect(str(self.request.cradmin_app.reverse_appindexurl()))
        status = status_models.Status.objects\
            .filter(period=self.request.cradmin_role)\
            .filter(status=status_models.Status.READY)\
            .order_by('-createtime').first()
        if status:
            return HttpResponseRedirect(str(self.request.cradmin_app.reverse_appurl(
                viewname='show-status',
                kwargs={
                    'roleid': self.request.cradmin_role.id
                }
            )))
        return super(QualificationPreviewView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context_data = super(QualificationPreviewView, self).get_context_data()
        context_data['period'] = self.request.cradmin_role
        context_data['plugintypeid'] = self.request.session['plugintypeid']
        context_data['table'] = self._get_tablebuilder(
                relatedstudents=self.get_relatedstudents_queryset(self.request.cradmin_role),
                qualifying_studentids=set(self.request.session['passing_relatedstudentids'])
        )

        return context_data

    def _create_status(self, plugintypeid, plugindata=None):
        """
        Creates and saves a entry in the database for current examqualification-status for students.

        Returns:
            A :obj:`~.devilry.devilry_qualifiesforexam.models.Status` instance.
        """
        status = status_models.Status.objects.create(
                status=status_models.Status.READY,
                period=self.request.cradmin_role,
                user=self.request.user,
                plugin=plugintypeid,
                plugin_data=plugindata
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
        plugindata = None
        try:
            if self.request.session['plugindata']:
                plugindata = self.request.session['plugindata']
                del self.request.session['plugindata']
        except KeyError:
            pass

        del self.request.session['passing_relatedstudentids']
        del self.request.session['plugintypeid']

        if 'save' in self.request.POST:
            status = self._create_status(plugintypeid, plugindata)
            self._bulk_create_relatedstudents(status, passing_relatedstudentids)
            return HttpResponseRedirect(str(self.request.cradmin_app.reverse_appurl(
                viewname='show-status',
                kwargs={
                    'roleid': self.request.cradmin_role.id,
                    'statusid': status.id
                }
            )))
        return super(QualificationPreviewView, self).form_valid(form)


class PrefetchStatusInfoMixin(object):
    """
    Mixin that joins and prefetches all the information we need of a
    :class:`~.devilry.deviry_qualifiesforexam.models.Status`.
    """
    def _get_qualifiesforexam_queryset(self):
        """
        Join :class:`~.devilry.apps.core.models.User` with
        :class:`~.devilry.deviry_qualifiesforexam.models.QualifiesForFinalExam`.

        Returns:
            QuerySet: of :obj:`~.devilry.deviry_qualifiesforexam.models.QualifiesForFinalExam`.
        """
        return status_models.QualifiesForFinalExam.objects\
            .select_related('relatedstudent__user')

    def _get_status(self, statusid):
        """
        Join tables for :class:`~.devilry.deviry_qualifiesforexam.models.Status` such as
        qualification results for the ``RelatedStudent``s on the period and their related user
        which info will be used.

        Args:
            statusid: Id of the Status to fetch.

        Returns:
            :obj:`~.devilry.deviry_qualifiesforexam.models.Status`: current status.
        """
        status = status_models.Status.objects\
            .select_related('period')\
            .prefetch_related(
                models.Prefetch(
                    'students',
                    queryset=self._get_qualifiesforexam_queryset()))\
            .get(id=statusid)
        return status


class QualificationStatusView(PrefetchStatusInfoMixin, AbstractQualificationPreviewView):
    """
    View for showing the current :class:`~.devilry.devilry_qualifiesforexam.models.Status` of the
    qualifications list.
    """
    template_name = 'devilry_qualifiesforexam/status_show.html'

    def get_context_data(self, **kwargs):
        context_data = super(QualificationStatusView, self).get_context_data(**kwargs)
        current_status = self._get_status(statusid=self.kwargs['statusid'])
        context_data['status'] = current_status
        context_data['required_assignments'] = None
        print(current_status.plugin_data)

        if current_status.plugin == 'devilry_qualifiesforexam_plugin_approved.plugin_select_assignments' and current_status.plugin_data:
            assignment_ids = json.loads(current_status.plugin_data)
            context_data['required_assignments'] = AssignmentListBuilderList.from_assignment_id_list(assignment_ids)


        # Add RelatedStudents to list and the IDs of the relatedstudents that qualify.
        qualifiesforexam = list(current_status.students.all())
        qualifying_studentids = [q.relatedstudent.id for q in qualifiesforexam if q.qualifies]
        relatedstudents = self.get_relatedstudents_queryset(self.request.cradmin_role)
        context_data['order_by_queryparam'] = self.get_order_by_queryparam()
        context_data['num_students_qualify'] = len(qualifying_studentids)
        context_data['num_students'] = len(relatedstudents)
        context_data['table'] = self._get_tablebuilder(
                relatedstudents=relatedstudents,
                qualifying_studentids=qualifying_studentids
        )
        return context_data


class PrintStatusView(PrefetchStatusInfoMixin, generic.TemplateView):
    """
    A printer-friendly view.

    Fetches students and presents a print-page of students that are qualified and not qualified to take the
    final exam.
    """
    template_name = 'devilry_qualifiesforexam/print_view.html'

    def get_order_by_queryparam(self):
        return self.request.GET.get('order_by', '')

    def get_order_by(self):
        order_by = self.get_order_by_queryparam()
        if order_by == 'fullname':
            return NullIf('relatedstudent__user__fullname', Value("")).asc(nulls_last=True)
        if order_by == 'username':
            return NullIf('relatedstudent__user__shortname', Value("")).asc(nulls_last=True)
        return NullIf('relatedstudent__user__lastname', Value("")).asc(nulls_last=True)

    def get_context_data(self, **kwargs):
        context_data = super(PrintStatusView, self).get_context_data(**kwargs)
        status = self._get_status(self.kwargs['statusid'])
        qualifying_students = []
        nonqualifying_students = []

        # Add qualifying and non-qualifying students
        order_by = self.get_order_by()
        for qualification in status.students.order_by(order_by, 'relatedstudent__user__shortname'):
            if qualification.qualifies:
                qualifying_students.append(qualification.relatedstudent)
            else:
                nonqualifying_students.append(qualification.relatedstudent)
        context_data['order_by_queryparam'] = self.get_order_by_queryparam()
        context_data['period'] = '{} ({})'.format(status.period.long_name, status.period)
        context_data['createtime'] = status.createtime
        context_data['qualifying_students'] = qualifying_students
        context_data['nonqualifying_students'] = nonqualifying_students
        return context_data


class RetractStatusForm(forms.ModelForm):
    """
    Form for providing a retracted-message for the status
    """
    class Meta:
        fields = ['message']
        model = status_models.Status
        help_texts = {
            'message': gettext_lazy('Provide a message as to why the Status needs to be retracted.')
        }

    def __init__(self, *args, **kwargs):
        super(RetractStatusForm, self).__init__(*args, **kwargs)
        self.fields['message'].required = True
        self.fields['message'].label = gettext_lazy('Message')

    @classmethod
    def get_field_layout(cls):
        return ['message']


class StatusRetractView(update.UpdateView):
    """
    Simple model-update view.

    Model-view for retracting a :obj:`~.devilry.deviry_qualifiesforexam.models.Status`
    """
    template_name = 'devilry_qualifiesforexam/retract_status.django.html'
    model = status_models.Status

    def get_pagetitle(self):
        return gettext_lazy('Why is the status retracted?')

    def get_buttons(self):
        buttons = [
            PrimarySubmit(self.get_submit_save_button_name(), self.get_submit_save_label())
        ]
        return buttons

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
        return gettext_lazy('Cannot retract status without a message.')
