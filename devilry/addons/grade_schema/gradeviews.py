from django import forms
from django.utils.translation import ugettext as _
from devilry.addons.examinerview.feedback_view import view_shortcut
from models import Entry, SchemaGradeResult
from django.forms.models import modelformset_factory
from django.forms.models import BaseModelFormSet


SchemaFormSet = modelformset_factory(SchemaGradeResult)

def view(request, delivery_obj):
    return view_shortcut(request, delivery_obj, ApprovedGrade,
            SchemaFormSet)
