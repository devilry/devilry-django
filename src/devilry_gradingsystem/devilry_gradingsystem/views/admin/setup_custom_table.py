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

# from devilry.apps.core.models import Assignment
# from devilry.apps.core.models import PointToGradeMap
from devilry.apps.core.models import PointRangeToGrade
from .base import AssignmentSingleObjectRequiresValidPluginMixin



def point_to_range_grade_form_factory(max_points):
    class PointRangeToGradeForm(forms.Form):
        minimum_points = forms.IntegerField(
            min_value=0,
            max_value=max_points,
            required=True)
        grade = forms.CharField(max_length=12, required=True)
    return PointRangeToGradeForm


class PointRangeToGradeFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(PointRangeToGradeFormSetHelper, self).__init__(*args, **kwargs)
        self.form_method = 'post'
        self.layout = Layout(
            'minimum_points',
            'grade',
        )
        self.add_input(Submit("submit", _("Save")))
        #self.render_required_fields = True


class SetupCustomTableView(AssignmentSingleObjectRequiresValidPluginMixin, DetailView):
    template_name = 'devilry_gradingsystem/admin/setup_custom_table.django.html'

    def get_formset_class(self):
        PointRangeToGradeForm = point_to_range_grade_form_factory(self.assignment.max_points)
        PointRangeToGradeFormSet = formset_factory(PointRangeToGradeForm,
            extra=6,
            max_num=6)
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
        PointRangeToGradeFormSet = self.get_formset_class()
        self.formset = PointRangeToGradeFormSet(initial=self.get_initial())
        return super(SetupCustomTableView, self).get(*args, **kwargs)

    def post(self, *args, **kwargs):
        self.object = self.get_object()
        self.assignment = self.object
        PointRangeToGradeFormSet = self.get_formset_class()
        self.formset = PointRangeToGradeFormSet(self.request.POST)
        if self.formset.is_valid():
            minimum_points_to_grade_list = []
            for valuedict in self.formset.cleaned_data:
                if valuedict: # We get empty valuedicts even when the form validates, so we have to skip those
                    minimum_points_to_grade_list.append(
                        (valuedict['minimum_points'], valuedict['grade']))
            minimum_points_to_grade_list.sort(lambda a, b: cmp(a[0], b[0]))
            point_to_grade_map = self.assignment.get_point_to_grade_map()
            point_to_grade_map.recreate_map(*minimum_points_to_grade_list)
            try:
                point_to_grade_map.clean()
            except ValidationError as e:
                self.validationerrors = e.messages
            else:
               pass
        return super(SetupCustomTableView, self).get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SetupCustomTableView, self).get_context_data(**kwargs)
        context['formset'] = self.formset
        context['formsethelper'] = PointRangeToGradeFormSetHelper()
        context['validationerrors'] = getattr(self, 'validationerrors', None)
        return context

    def get_success_url(self):
        # TODO: Check if passing_grade_min_points is needed
        return reverse('devilry_gradingsystem_admin_summary', kwargs={
            'assignmentid': self.object.id
        })

