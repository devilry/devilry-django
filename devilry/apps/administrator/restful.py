from ...restful import restful_modelapi, ModelRestfulView, RestfulManager
from simplified import (SimplifiedNode, SimplifiedSubject, SimplifiedPeriod,
                        SimplifiedAssignment, SimplifiedAssignmentGroup,
                        SimplifiedDelivery)
from ..extjshelpers import extjs_restful_modelapi


__all__ = ('RestfulSimplifiedNode', 'RestfulSimplifiedSubject',
           'RestfulSimplifiedPeriod', 'RestfulSimplifiedAssignment',
           'RestfulSimplifiedAssignmentGroup', 'RestfulSimplifiedDelivery')


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
        combobox_tpl = ('<div class="important">{short_name}</div>'
                        '<div class="unimportant">{long_name}</div>')


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
        combobox_tpl = ('<div class="important">{parentnode__short_name}.{short_name}</div>'
                        '<div class="unimportant">{long_name}</div>')
        combobox_displayfield = 'short_name'


@administrator_restful.register
@extjs_restful_modelapi
@restful_modelapi
class RestfulSimplifiedAssignment(ModelRestfulView):
    class Meta:
        simplified = SimplifiedAssignment
        foreignkey_fields = {'parentnode__id': RestfulSimplifiedPeriod}

    class ExtjsModelMeta:
        """ Metadata for javascript. """
        combobox_fieldgroups = ['subject', 'period']
        combobox_tpl = ('<div class="important">{parentnode__parentnode__short_name}.{parentnode__short_name}.{short_name}</div>'
                        '<div class="unimportant">{long_name}</div>')
        combobox_displayfield = 'short_name'


@administrator_restful.register
@extjs_restful_modelapi
@restful_modelapi
class RestfulSimplifiedAssignmentGroup(ModelRestfulView):
    class Meta:
        simplified = SimplifiedAssignmentGroup
        foreignkey_fields = {'parentnode__id': RestfulSimplifiedAssignment}

    class ExtjsModelMeta:
        """ Metadata for javascript. """
        combobox_fieldgroups = ['assignment', 'period', 'subject']
        combobox_tpl = ('<div class="important">{parentnode__parentnode__parentnode__short_name}.{parentnode__parentnode__short_name}.{parentnode__short_name} (group id: {id})</div>')
        combobox_displayfield = 'id'


@administrator_restful.register
@extjs_restful_modelapi
@restful_modelapi
class RestfulSimplifiedDelivery(ModelRestfulView):
    class Meta:
        simplified = SimplifiedDelivery
        foreignkey_fields = {'parentnode__id': RestfulSimplifiedAssignmentGroup}

    class ExtjsModelMeta:
        """ Metadata for javascript. """
        combobox_fieldgroups = ['assignment', 'period', 'subject',
                                'assignment_group']
        combobox_tpl = ('<div class="important">Delivery: {number} '
                        '(group: {assignment_group__id}'
                        '<tpl if="assignment_group__name"> &ndash; {assignment_group__name}</tpl>'
                        '<tpl for="assignment_group__candidates__identifier">, {.}</tpl>'
                        ')</div>'
                        '<div class="unimportant">{assignment_group__parentnode__parentnode__parentnode__short_name}'
                        '.{assignment_group__parentnode__parentnode__short_name}.'
                        '{assignment_group__parentnode__short_name}</div>')
        combobox_displayfield = 'id'
