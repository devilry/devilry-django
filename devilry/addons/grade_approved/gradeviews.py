from django import forms
from django.utils.translation import ugettext as _
from devilry.examinerview.feedback_view import view_shortcut
from models import ApprovedGrade


class ApprovedGradeForm(forms.ModelForm):
    class Meta:
        model = ApprovedGrade
        fields = ('approved',)

def view(request, delivery_obj):
    return view_shortcut(request, delivery_obj, ApprovedGrade,
            ApprovedGradeForm)
