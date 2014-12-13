from django.utils.translation import ugettext_lazy as _
from extjs4.views import Extjs4AppView
from django.views.generic import TemplateView
from django.http import HttpResponseNotFound
from django.http import HttpResponseForbidden
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field
from devilry.apps.core.models import Period
from devilry.devilry_qualifiesforexam.models import Status


class AppView(Extjs4AppView):
    template_name = "devilry_qualifiesforexam/app.django.html"
    appname = 'devilry_qualifiesforexam'
    title = _('Devilry - Qualifies for final exam')




class StatusPrintViewForm(forms.Form):
    sortby = forms.ChoiceField(
            label=_('Sort by'),
            choices=(
                ('name', _('Name')),
                ('username', _('Username')),
                ('lastname', _('Last name')))
            )

    def __init__(self, *args, **kwargs):
        super(StatusPrintViewForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.form_id = 'sortform'
        self.helper.form_method = 'get'
        self.helper.layout = Layout(
                Field('sortby', id='sortby-field')
        )


def extract_lastname(user):
    profile = user.devilryuserprofile
    name = profile.full_name
    if not name or not name.strip():
        return ''
    return name.rsplit(' ', 1)[-1]

def cmp_lastname(user_a, user_b):
    return cmp(extract_lastname(user_a), extract_lastname(user_b))

class StatusPrintView(TemplateView):
    template_name = 'devilry_qualifiesforexam/statusprint.django.html'
    cookiekey = 'devilry_qualifiesforexam.statusprint.sortby'

    def get(self, request, status_id):
        try:
            self.status = Status.objects.get(pk=status_id)
        except Status.DoesNotExist:
            return HttpResponseNotFound()
        else:
            if not Period.where_is_admin_or_superadmin(self.request.user).filter(id=self.status.period_id).exists():
                return HttpResponseForbidden()
            elif self.status.status != Status.READY:
                return HttpResponseNotFound()
            else:
                response = super(StatusPrintView, self).get(request, status_id)
                response.set_cookie(self.cookiekey, self.sortby)
                return response

    @classmethod
    def get_studentstatuses_by_sorter(cls, status, sortby):
        if sortby == 'name':
            orderby = 'relatedstudent__user__devilryuserprofile__full_name'
        elif sortby == 'username' or sortby == 'lastname':
            orderby = 'relatedstudent__user__username'
        else:
            raise ValueError('Invalid sortby: {0}'.format(sortby))

        studentstatuses = status.students.all().order_by(orderby)
        studentstatuses = studentstatuses.select_related(
                'relatedstudent',
                'relatedstudent__user',
                'relatedstudent__user__devilryuserprofile'
            )
        if sortby == 'lastname':
            studentstatuses = list(studentstatuses)
            studentstatuses.sort(lambda a, b: cmp_lastname(a.relatedstudent.user, b.relatedstudent.user))
        return studentstatuses

    def get_context_data(self, **kwargs):
        context = super(StatusPrintView, self).get_context_data(**kwargs)
        sortby = self.request.COOKIES.get(self.cookiekey, 'name')
        if self.request.GET.get('sortby'):
            form = StatusPrintViewForm(self.request.GET)
            if form.is_valid():
                sortby = form.cleaned_data['sortby']
        else:
            form = StatusPrintViewForm(initial={'sortby': sortby})
        studentstatuses = self.__class__.get_studentstatuses_by_sorter(self.status, sortby)
        self.sortby = sortby
        context['status'] = self.status
        context['studentstatuses'] = studentstatuses
        context['form'] = form
        return context
