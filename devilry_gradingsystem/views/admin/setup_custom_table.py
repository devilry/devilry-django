from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.views.generic import DetailView
from django.core.exceptions import ValidationError
from django import forms
from django.forms.formsets import formset_factory
from django.utils.translation import ugettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
# from crispy_forms.layout import Field
from crispy_forms.layout import Submit
# from crispy_forms.layout import ButtonHolder

from devilry.apps.core.models import PointRangeToGrade
from devilry.apps.core.models.pointrange_to_grade import DuplicateGradeError
from .base import AssignmentSingleObjectRequiresValidPluginMixin



def point_to_range_grade_form_factory(max_points):
    class PointRangeToGradeForm(forms.Form):
        grade = forms.CharField(max_length=12, required=False)
        minimum_points = forms.IntegerField(
            min_value=0,
            max_value=max_points,
            required=False)
    return PointRangeToGradeForm


class PointRangeToGradeFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(PointRangeToGradeFormSetHelper, self).__init__(*args, **kwargs)
        self.form_tag = False
        self.layout = Layout(
            'grade',
            'minimum_points',
        )
        self.template = 'bootstrap/table_inline_formset.html'


class SetupCustomTableView(AssignmentSingleObjectRequiresValidPluginMixin, DetailView):
    template_name = 'devilry_gradingsystem/admin/setup_custom_table.django.html'

    def get_formset_class(self, extra=0):
        PointRangeToGradeForm = point_to_range_grade_form_factory(self.assignment.max_points)
        PointRangeToGradeFormSet = formset_factory(PointRangeToGradeForm,
            extra=extra)
        return PointRangeToGradeFormSet

    def get_initial(self):
        initial = []
        for pointrange in self.assignment.get_point_to_grade_map().pointrangetograde_set.all():
            initial.append({
                'minimum_points': pointrange.minimum_points,
                'grade': pointrange.grade
            })
        return initial

    def get(self, *args, **kwargs):
        self.object = self.get_object()
        self.assignment = self.object
        initial = self.get_initial()
        if initial:
            extra = 0
        else:
            extra = 6
        PointRangeToGradeFormSet = self.get_formset_class(extra=extra)
        self.formset = PointRangeToGradeFormSet(initial=initial)
        return super(SetupCustomTableView, self).get(*args, **kwargs)

    def post(self, *args, **kwargs):
        self.object = self.get_object()
        self.assignment = self.object
        add_rows = 'submit_add_rows' in self.request.POST
        postdata = self.request.POST
        if add_rows:
            postdata = postdata.copy()
            postdata['form-TOTAL_FORMS'] = int(postdata['form-TOTAL_FORMS']) + 3
        PointRangeToGradeFormSet = self.get_formset_class()
        self.formset = PointRangeToGradeFormSet(postdata)

        if not add_rows:
            if self.formset.is_valid():
                minimum_points_to_grade_list = []
                for valuedict in self.formset.cleaned_data:
                    if valuedict and len(valuedict) == 2:
                        minimum_points_to_grade_list.append(
                            (valuedict['minimum_points'], valuedict['grade']))
                minimum_points_to_grade_list.sort(lambda a, b: cmp(a[0], b[0]))
                point_to_grade_map = self.assignment.get_point_to_grade_map()
                try:
                    point_to_grade_map.recreate_map(*minimum_points_to_grade_list)
                except DuplicateGradeError as e:
                    self.validationerrors = [e.message]
                else:
                    try:
                        point_to_grade_map.clean()
                    except ValidationError as e:
                        self.validationerrors = e.messages
                    else:
                        point_to_grade_map.save()
                        return redirect(self.get_success_url())
        return super(SetupCustomTableView, self).get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SetupCustomTableView, self).get_context_data(**kwargs)
        context['formset'] = self.formset
        context['formsethelper'] = PointRangeToGradeFormSetHelper()
        context['validationerrors'] = getattr(self, 'validationerrors', None)
        context['current_step'] = self.get_wizard_step_map().get_by_slug('setup_custom_table')
        return context

    def get_success_url(self):
        viewname = 'devilry_gradingsystem_admin_setpassing_grade_min_points'
        return reverse(viewname, kwargs={
            'assignmentid': self.object.id
        })