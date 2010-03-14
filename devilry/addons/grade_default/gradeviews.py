from django import forms
from django.utils.translation import ugettext as _
from devilry.addons.examiner.feedback_view import view_shortcut
from models import CharFieldGrade


class CharFieldGradeForm(forms.ModelForm):
    class Meta:
        model = CharFieldGrade
        fields = ('grade',)

def view(request, delivery_obj):
    return view_shortcut(request, delivery_obj, CharFieldGrade,
            CharFieldGradeForm)
