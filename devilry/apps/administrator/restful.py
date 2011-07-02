from django import forms

from ...restful import restful_modelapi, ModelRestView
from simplified import Node, Subject, Period


__all__ = ('RestNode', 'RestSubject', 'RestPeriod')


@restful_modelapi
class RestNode(ModelRestView):
    class Meta:
        simplified = Node


@restful_modelapi
class RestSubject(ModelRestView):
    class Meta:
        simplified = Subject


@restful_modelapi
class RestPeriod(ModelRestView):
    class Meta:
        simplified = Period

    class EditForm(forms.ModelForm):
        model = Period._meta.model
        fields = Period._meta.resultfields.aslist('subject')
