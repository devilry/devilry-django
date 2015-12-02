from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field
from django.shortcuts import redirect
from django_cradmin import crapp
from django_cradmin.viewhelpers import objecttable, update
from django.db import models
from django.utils.translation import ugettext_lazy as _, ugettext_lazy
from devilry.devilry_account.models import UserEmail
from devilry.devilry_qualifiesforexam.models import QualifiesForFinalExam, Status
from django.views.generic import TemplateView
from devilry.devilry_student.cradminextensions.columntypes import BooleanYesNoColumn
from django.http import HttpResponseNotFound
from django.http import HttpResponseForbidden
from django import forms


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

    def post(self, *args, **kwargs):
        app = self.request.cradmin_app
        status = Status.objects.get(period=self.request.cradmin_role)
        status.status = Status.READY
        status.full_clean()
        status.save()
        return redirect(app.reverse_appurl('step4'))


class ListViewStep4(ListViewMixin):
    template_name = "devilry_admin/period/qualifiedforfinalexams/step4.django.html"

    def get_pagetitle(self):
        return _('Qualified for final exams')

    def get_buttons(self):
        app = self.request.cradmin_app
        self.status = Status.objects.get(period=self.request.cradmin_role)
        return [
            objecttable.Button(
                label=ugettext_lazy('Print'),
                url=app.reverse_appurl("step4-print", args=[self.status.id]),
                buttonclass='btn btn-primary'),
            objecttable.Button(
                label=ugettext_lazy('Update'),
                url=app.reverse_appurl(crapp.INDEXVIEW_NAME)),
            objecttable.Button(
                label=ugettext_lazy('Retract'),
                url=app.reverse_appurl('step4-retraction', args=[self.status.id]))
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

    def set_automatic_attributes(self, obj):
        super(RetractionView, self). set_automatic_attributes(obj)
        obj.status = Status.NOTREADY

    # It is necessary to check the permission before retracting
    # En la plantilla: action="{% cradmin_appurl "myview" pk=status.id %}"


class PrintQualifiedStudentsViewForm(forms.Form):
    sortby = forms.ChoiceField(
            label=_('Sort by'),
            choices=(
                ('name', _('Name')),
                ('username', _('Username')),
                ('lastname', _('Last name')))
            )

    def __init__(self, *args, **kwargs):
        super(PrintQualifiedStudentsViewForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.form_id = 'sortform'
        self.helper.form_method = 'get'
        self.helper.layout = Layout(
                Field('sortby', id='sortby-field')
        )


def extract_lastname(user):
    return user.lastname


def cmp_lastname(user_a, user_b):
    return cmp(extract_lastname(user_a), extract_lastname(user_b))


class PrintQualifiedStudentsView(TemplateView):
    template_name = 'devilry_admin/period/qualifiedforfinalexams/statusprint.django.html'
    cookiekey = 'devilry_qualifiesforexam.statusprint.sortby'

    def get(self, request, status_id):
        try:
            self.status = Status.objects.get(pk=status_id)
        except Status.DoesNotExist:
            return HttpResponseNotFound()
        else:
            #if not Period.where_is_admin_or_superadmin(self.request.user).filter(id=self.status.period_id).exists():
             #   return HttpResponseForbidden()
           # el
            if self.status.status != Status.READY:
                return HttpResponseNotFound()
            else:
                response = super(PrintQualifiedStudentsView, self).get(request, status_id)
                response.set_cookie(self.cookiekey, self.sortby)
                return response

    @classmethod
    def get_studentstatuses_by_sorter(cls, status, sortby):
        if sortby == 'name':
            orderby = 'relatedstudent__user__fullname'
        elif sortby == 'username' or sortby == 'lastname':
            orderby = 'relatedstudent__user__shortname'
        else:
            raise ValueError('Invalid sortby: {0}'.format(sortby))

        studentstatuses = status.students.all().order_by(orderby)
        studentstatuses = studentstatuses.select_related('relatedstudent', 'relatedstudent__user')
        if sortby == 'lastname':
            studentstatuses = list(studentstatuses)
            studentstatuses.sort(lambda a, b: cmp_lastname(a.relatedstudent.user, b.relatedstudent.user))
        return studentstatuses

    def get_context_data(self, **kwargs):
        context = super(PrintQualifiedStudentsView, self).get_context_data(**kwargs)
        sortby = self.request.COOKIES.get(self.cookiekey, 'name')
        if self.request.GET.get('sortby'):
            form = PrintQualifiedStudentsViewForm(self.request.GET)
            if form.is_valid():
                sortby = form.cleaned_data['sortby']
        else:
            form = PrintQualifiedStudentsViewForm(initial={'sortby': sortby})
        studentstatuses = self.__class__.get_studentstatuses_by_sorter(self.status, sortby)
        self.sortby = sortby
        context['status'] = self.status
        context['studentstatuses'] = studentstatuses
        context['form'] = form
        return context


class Overview(TemplateView):
    template_name = 'devilry_admin/dashboard/overview.django.html'


class App(crapp.App):
    appurls = [
        crapp.Url(r'^$', Overview.as_view(), name=crapp.INDEXVIEW_NAME),
        crapp.Url(r'^step3$', ListViewStep3.as_view(), name="step3"),
        crapp.Url(r'^step4$', ListViewStep4.as_view(), name="step4"),
        crapp.Url(r'^step4-retraction/(?P<pk>\d+)$', RetractionView.as_view(), name="step4-retraction"),
        crapp.Url(r'^step4-print-results/(?P<status_id>\d+)$', PrintQualifiedStudentsView.as_view(), name="step4-print"),
    ]


