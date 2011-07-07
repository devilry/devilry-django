from ...restful import restful_modelapi, ModelRestfulView, RestfulManager
from simplified import (SimplifiedNode, SimplifiedSubject, SimplifiedPeriod,
                        SimplifiedAssignment)
from ..extjshelpers import extjs_restful_modelapi


__all__ = ('RestfulSimplifiedNode', 'RestfulSimplifiedSubject', 'RestfulSimplifiedPeriod')


administrator_restful = RestfulManager()

@administrator_restful.register
@extjs_restful_modelapi
@restful_modelapi
class RestfulSimplifiedNode(ModelRestfulView):
    class Meta:
        simplified = SimplifiedNode
        foreignkey_fields = {'parentnode__id': 'RestfulSimplifiedNode'}

    class ExtjsModelMeta:
        combobox_displayfield = 'short_name'
        combobox_tpl = ('<div class="unimportant">{long_name}</div>'
                        '<div class="important">{short_name}</div>')


@administrator_restful.register
@extjs_restful_modelapi
@restful_modelapi
class RestfulSimplifiedSubject(ModelRestfulView):
    class Meta:
        simplified = SimplifiedSubject
        foreignkey_fields = {'parentnode__id': RestfulSimplifiedNode}

    class ExtjsModelMeta:
        """ Metadata for javascript. """
        combobox_tpl = RestfulSimplifiedNode.ExtjsModelMeta.combobox_tpl
        combobox_displayfield = 'short_name'


@administrator_restful.register
@extjs_restful_modelapi
@restful_modelapi
class RestfulSimplifiedPeriod(ModelRestfulView):
    class Meta:
        simplified = SimplifiedPeriod
        foreignkey_fields = {'parentnode__id': RestfulSimplifiedSubject}

    class ExtjsModelMeta:
        """ Metadata for javascript. """
        combobox_fieldgroups = ['subject']
        combobox_tpl = ('<span class="important">{long_name}</span><br/>'
                        '<span class="unimportant">{parentnode__short_name}.{short_name}</span>')


@administrator_restful.register
@extjs_restful_modelapi
@restful_modelapi
class RestfulSimplifiedAssignment(ModelRestfulView):
    class Meta:
        simplified = SimplifiedAssignment
        foreignkey_fields = {'parentnode__id': RestfulSimplifiedSubject}

    class ExtjsModelMeta:
        """ Metadata for javascript. """
        combobox_fieldgroups = ['subject']
        combobox_tpl = ('<span class="important">{long_name}</span><br/>'
                        '<span class="unimportant">{parentnode__short_name}.{short_name}</span>')
