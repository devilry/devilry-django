from django.contrib import messages
from django.contrib.auth import get_user_model
from django import forms
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.views.generic.edit import BaseFormView

from django_cradmin import crapp
from django_cradmin.viewhelpers import objecttable, update
from django.db import models
from django.utils.translation import ugettext_lazy as _
from devilry.devilry_account.models import UserEmail
from devilry.devilry_admin.views.common import userselect_common
from devilry.devilry_qualifiesforexam.models import QualifiesForFinalExam, Status
from django.views.generic import TemplateView
from devilry.devilry_student.cradminextensions.columntypes import BooleanYesNoColumn


class GetQuerysetForRoleMixin(object):
    model = QualifiesForFinalExam

    def get_queryset_for_role(self, role):
        period = role
        return self.model.objects \
            .filter(status__period=period) \
            .order_by('relatedstudent__user__fullname')


class UserInfoColumn(objecttable.PlainTextColumn):
    modelfield = 'id'
    template_name = 'devilry_admin/period/qualifiedforfinalexams/userlistview-info-column.django.html'
    orderingfield = 'relatedstudent__user__fullname'

    def get_header(self):
        return _('Students')

    def get_context_data(self, obj):
        context = super(UserInfoColumn
            , self).get_context_data(obj=obj)
        context['rel_user'] = obj.relatedstudent.user
        return context


class QualifiesColumn(BooleanYesNoColumn):
    # Espen asked me to create a BooleanColumn, but I found out that was already created. Maybe needs translations
    modelfield = 'qualifies'
    template_name = 'devilry_admin/period/qualifiedforfinalexams/statuslistview-info-column.django.html'

    def get_header(self):
        return _('Is qualified for the final exam?')

    def get_context_data(self, obj):
        context = super(QualifiesColumn, self).get_context_data(obj=obj)
        context['status'] = obj.qualifies
        return context


class ListViewMixin(GetQuerysetForRoleMixin, objecttable.ObjectTableView):
    searchfields = ['relatedstudent__user__shortname', 'relatedstudent__user__fullname', 'qualifies']
    hide_column_headers = False
    columns = [UserInfoColumn, QualifiesColumn]

    def get_queryset_for_role(self, role):
        return super(ListViewMixin, self).get_queryset_for_role(role) \
            .prefetch_related(
            models.Prefetch('relatedstudent__user__useremail_set',
                            queryset=UserEmail.objects.filter(is_primary=True),
                            to_attr='primary_useremail_objects'))

    def get_no_items_message(self):
        """
        Get the message to show when there are no items.
        """
        return _('There is no students registered for %(what)s.') % {
            'what': self.request.cradmin_role.get_path()
        }


class ListViewStep3(ListViewMixin):
    template_name = "devilry_admin/period/qualifiedforfinalexams/step3.django.html"

    def get_pagetitle(self):
        return _('Preview and confirm')

    def post(self, *args, **kwargs):
        app = self.request.cradmin_app
        status = self.get_queryset()[0].status
        status.status = 'ready'
        status.save()
        return redirect(app.reverse_appurl('step4'))


class ListViewStep4(ListViewMixin):
    template_name = "devilry_admin/period/qualifiedforfinalexams/step4.django.html"

    def get_pagetitle(self):
        return _('Qualified for final exams')

    def post(self, *args, **kwargs):
        app = self.request.cradmin_app
        return redirect(app.reverse_appurl(crapp.INDEXVIEW_NAME))


class StatusRetractView(TemplateView):
    def post(self, *args, **kwargs):
        pass


class PrintQualifiedStudentsView(TemplateView):
    def get(self, *args, **kwargs):
        pass


class Overview(TemplateView):
    template_name = 'devilry_admin/dashboard/overview.django.html'


class App(crapp.App):
    appurls = [
        crapp.Url(r'^$', Overview.as_view(), name=crapp.INDEXVIEW_NAME),
        crapp.Url(r'^step3', ListViewStep3.as_view(), name="step3"),
        crapp.Url(r'^step4', ListViewStep4.as_view(), name="step4"),
        crapp.Url(r'^step4-retraction', StatusRetractView.as_view(), name="step4-retraction")
    ]


