from django.views.generic import DetailView
from django.shortcuts import redirect
from django.http import Http404

from devilry.apps.core.models import Assignment
from devilry_examiner.forms import GroupIdsForm


class AddDeadlineForm(GroupIdsForm):
    deadline = forms.DateTimeField()
    def clean(self):
        cleaned_data = super(AddDeadlineGroupIdsForm, self).clean()
        deadline = cleaned_data.get('deadline')
        if deadline and hasattr(self, 'cleaned_groups'):
            if cleaned_groups.filter(last_deadline__gt=deadline).exists():
               raise forms.ValidationError('The last deadline of one or more of the selected groups is after the selected deadline.')
       return cleaned_data


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

    def post(self, *args, **kwargs):
        self.object = self.get_object()
        self.assignment = self.object
        if 'submit_add_deadline' in self.request.POST:
            pass
        else:
            idsform = GroupIdsForm(self.request.POST,
                assignment=self.assignment
                user=self.request.user)
            if idsform.is_valid():
                self.groups = idsform.cleaned_groups
            else:
                raise Http404
        return super(SingleDeliveryView, self).get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SingleDeliveryView, self).get_context_data(**kwargs)
        context['form'] = self.form
        return context