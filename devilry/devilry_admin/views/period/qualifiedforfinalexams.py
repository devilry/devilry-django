from django.shortcuts import redirect
from django_cradmin import crapp
from django_cradmin.viewhelpers import objecttable, update
from django.db import models
from django.utils.translation import ugettext_lazy as _, ugettext_lazy
from devilry.devilry_account.models import UserEmail
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
        context = super(UserInfoColumn, self).get_context_data(obj=obj)
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

    def get_buttons(self):
        app = self.request.cradmin_app
        return [
            objecttable.Button(
                label=ugettext_lazy('Confirm'),
                url=app.reverse_appurl('step4'))
        ]

    def post(self, *args, **kwargs):
        app = self.request.cradmin_app
        Status.objects.filter(period=self.request.cradmin_role).update(status='ready')
        return redirect(app.reverse_appurl('step4'))


class ListViewStep4(ListViewMixin):
    template_name = "devilry_admin/period/qualifiedforfinalexams/step4.django.html"

    def get_pagetitle(self):
        return _('Qualified for final exams')

    def get_buttons(self):
        app = self.request.cradmin_app
        return [
            objecttable.Button(
                label=ugettext_lazy('Update'),
                url=app.reverse_appurl(crapp.INDEXVIEW_NAME),
                buttonclass='btn btn-primary'),
            objecttable.Button(
                label=ugettext_lazy('Retract'),
                url=app.reverse_appurl('step4-retraction'),
                buttonclass='btn btn-primary'),
            objecttable.Button(
                label=ugettext_lazy('Print'),
                url=app.reverse_appurl("step4-print"),
                buttonclass='btn btn-primary')
        ]

    def post(self, *args, **kwargs):
        app = self.request.cradmin_app
        return redirect(app.reverse_appurl(crapp.INDEXVIEW_NAME))


class RetractionView(update.UpdateView):
    model = Status
    fields = ['message']
    submit_save_label = ugettext_lazy('Save')

    def get_queryset_for_role(self, role):
        return Status.objects.filter(period=self.request.cradmin_role)

    # def get_success_url(self):
    #     app = self.request.cradmin_app
    #     return redirect(app.reverse_appurl(crapp.INDEXVIEW_NAME))

    # def set_automatic_attributes(self, obj):
    #     super(RetractionView, self). set_automatic_attributes(obj)
    #     obj.status = 'notready'
    #     #obj.save()

    # It is necessary to check the permission before retracting
    # En la plantilla: action="{% cradmin_appurl "myview" pk=status.id %}"


class PrintQualifiedStudentsView(TemplateView):
    template_name = 'devilry_admin/dashboard/overview.django.html'


class Overview(TemplateView):
    template_name = 'devilry_admin/dashboard/overview.django.html'


class App(crapp.App):
    appurls = [
        crapp.Url(r'^$', Overview.as_view(), name=crapp.INDEXVIEW_NAME),
        crapp.Url(r'^step3', ListViewStep3.as_view(), name="step3"),
        crapp.Url(r'^step4', ListViewStep4.as_view(), name="step4"),
        crapp.Url(r'^step4-retraction', RetractionView.as_view(), name="step4-retraction"),
        crapp.Url(r'^step4-print-results', PrintQualifiedStudentsView.as_view(), name="step4-print"),
    ]


