from ...restful import restful_modelapi, ModelRestfulView, RestfulManager
from simplified import (SimplifiedNode, SimplifiedSubject, SimplifiedPeriod,
                        SimplifiedAssignment, SimplifiedAssignmentGroup,
                        SimplifiedDelivery, SimplifiedDeadline,
                        SimplifiedStaticFeedback, SimplifiedFileMeta)
from ..extjshelpers import extjs_restful_modelapi#, wizard
from devilry.coreutils.restful import metabases as restfulmetabases


__all__ = ('RestfulSimplifiedNode', 'RestfulSimplifiedSubject',
           'RestfulSimplifiedPeriod', 'RestfulSimplifiedAssignment',
           'RestfulSimplifiedAssignmentGroup', 'RestfulSimplifiedDelivery',
           'RestfulSimplifiedDeadline', 'RestfulSimplifiedFileMeta',
           'RestfulSimplifiedStaticFeedback')


administrator_restful = RestfulManager()

@administrator_restful.register
@extjs_restful_modelapi
@restful_modelapi
class RestfulSimplifiedNode(ModelRestfulView):
    class Meta:
        simplified = SimplifiedNode
        foreignkey_fields = {'parentnode': 'RestfulSimplifiedNode'}

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
        foreignkey_fields = {'parentnode': RestfulSimplifiedNode}

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
        foreignkey_fields = {'parentnode': RestfulSimplifiedSubject}

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
        foreignkey_fields = {'parentnode': RestfulSimplifiedPeriod}

    class ExtjsModelMeta(restfulmetabases.AssignmentExtjsModelMeta):
        """ Metadata for javascript. """
        #wizard = wizard.Wizards(
                #wizard.Wizard("Simple obligatory assignment",
                               #("An assignment where each student is corrected "
                                #"by a single examiner."),
                               #wizard.Page(fields=['parentnode', 'publishing_time']))
            #)

@administrator_restful.register
@extjs_restful_modelapi
@restful_modelapi
class RestfulSimplifiedAssignmentGroup(ModelRestfulView):
    class Meta:
        simplified = SimplifiedAssignmentGroup
        foreignkey_fields = {'parentnode': RestfulSimplifiedAssignment}

    class ExtjsModelMeta(restfulmetabases.AssignmentGroupExtjsModelMeta):
        """ Metadata for javascript. """


@administrator_restful.register
@extjs_restful_modelapi
@restful_modelapi
class RestfulSimplifiedDeadline(ModelRestfulView):
    class Meta:
        simplified = SimplifiedDeadline
        foreignkey_fields = {'assignment_group': RestfulSimplifiedAssignmentGroup}


@administrator_restful.register
@extjs_restful_modelapi
@restful_modelapi
class RestfulSimplifiedDelivery(ModelRestfulView):
    class Meta:
        simplified = SimplifiedDelivery
        foreignkey_fields = {'deadline': RestfulSimplifiedDeadline}

    class ExtjsModelMeta(restfulmetabases.DeliveryExtjsModelMeta):
        """ Metadata for javascript. """


@administrator_restful.register
@extjs_restful_modelapi
@restful_modelapi
class RestfulSimplifiedStaticFeedback(ModelRestfulView):
    class Meta:
        simplified = SimplifiedStaticFeedback
        foreignkey_fields = {'delivery': RestfulSimplifiedDelivery}


@administrator_restful.register
@extjs_restful_modelapi
@restful_modelapi
class RestfulSimplifiedFileMeta(ModelRestfulView):
    class Meta:
        simplified = SimplifiedFileMeta
        foreignkey_fields = {'delivery': RestfulSimplifiedDelivery}
