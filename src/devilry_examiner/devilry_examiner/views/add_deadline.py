from django.views.generic.detail import DetailView
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from crispy_forms.layout import Field
from crispy_forms.layout import Submit
from crispy_forms.layout import Hidden
from crispy_forms.layout import ButtonHolder

from devilry.apps.core.models import Assignment
from devilry_examiner.forms import GroupIdsForm



class AddDeadlineForm(GroupIdsForm):
    deadline = forms.DateTimeField()
    text = forms.CharField(required=False)

    def clean(self):
        cleaned_data = super(AddDeadlineForm, self).clean()
        deadline = cleaned_data.get('deadline')
        if deadline and hasattr(self, 'cleaned_groups'):
            if self.cleaned_groups.filter(last_deadline__deadline__gt=deadline).exists():
                raise forms.ValidationError('The last deadline of one or more of the selected groups is after the selected deadline.')
        return cleaned_data

    def __init__(self, *args, **kwargs):
        super(AddDeadlineForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'deadline',
            'text',
            'group_ids',
            ButtonHolder(
                Submit('submit_add_deadline', _('Add deadline'))
            )
        )



class AddDeadlineView(DetailView):
    template_name = "devilry_examiner/add_deadline.django.html"
    model = Assignment
    pk_url_kwarg = 'assignmentid'
    context_object_name = 'assignment'

    def get_queryset(self):
        return Assignment.objects.filter_examiner_has_access(self.request.user)\
            .select_related(
                'parentnode', # Period
                'parentnode__parentnode') # Subject

    def get_success_url(self):
        return reverse('devilry_examiner_allgroupsoverview', kwargs={'assignmentid': self.object.id})

    def get_initial_formdata(self):
        """
        Get the initial POST data - only here to make the redirect from get() to post() possible.
        """
        if self.request.method == 'POST':
            return self.request.POST
        else:
            return self.request.GET

    def form_valid(self, form):
        print
        print 'Create deadline on:'
        for group in form.cleaned_groups:
            print group
        print
        return redirect(self.get_success_url())

    def get(self, *args, **kwargs):
        # Redirect to POST to make it easier to debug/play with the initial post data
        return self.post(*args, **kwargs)

    def post(self, *args, **kwargs):
        self.object = self.get_object()
        assignment = self.object
        common_form_kwargs = dict(assignment=assignment, user=self.request.user)
        if not 'submit_add_deadline' in self.get_initial_formdata():
            # When redirected from another view like allgroupview with a list of group_ids
            # - we use a GroupIdsForm to parse the list 
            groupidsform = GroupIdsForm(self.get_initial_formdata(), **common_form_kwargs)
            if groupidsform.is_valid():
                self.form = AddDeadlineForm(
                    initial={'group_ids': groupidsform.cleaned_data['group_ids']},
                    **common_form_kwargs)
            else:
                raise Http404
        else:
            self.form = AddDeadlineForm(self.request.POST, **common_form_kwargs)
            if self.form.is_valid():
                return self.form_valid(self.form)
        return super(AddDeadlineView, self).get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(AddDeadlineView, self).get_context_data(**kwargs)
        context['form'] = self.form
        return context