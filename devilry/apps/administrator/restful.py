from ...restful import restful_modelapi, ModelRestfulView, RestfulManager
from simplified import (SimplifiedNode, SimplifiedSubject, SimplifiedPeriod,
                        SimplifiedRelatedExaminer, SimplifiedRelatedStudent,
                        SimplifiedAssignment, SimplifiedAssignmentGroup,
                        SimplifiedDelivery, SimplifiedDeadline,
                        SimplifiedStaticFeedback, SimplifiedFileMeta)
from ..extjshelpers import extjs_restful_modelapi
from devilry.coreutils.restful import metabases as restfulmetabases
from devilry.restful.fields import JsonListWithFallbackField


__all__ = ('RestfulSimplifiedNode', 'RestfulSimplifiedSubject',
           'RestfulSimplifiedPeriod',
           'RestfulSimplifiedRelatedExaminer', 'RestfulSimplifiedRelatedStudent',
           'RestfulSimplifiedAssignment',
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
class RestfulSimplifiedRelatedExaminer(ModelRestfulView):
    class Meta:
        simplified = SimplifiedRelatedExaminer
        foreignkey_fields = {'period': RestfulSimplifiedPeriod}


@administrator_restful.register
@extjs_restful_modelapi
@restful_modelapi
class RestfulSimplifiedRelatedStudent(ModelRestfulView):
    class Meta:
        simplified = SimplifiedRelatedStudent
        foreignkey_fields = {'period': RestfulSimplifiedPeriod}


@administrator_restful.register
@extjs_restful_modelapi
@restful_modelapi
class RestfulSimplifiedAssignment(ModelRestfulView):
    class Meta:
        simplified = SimplifiedAssignment
        foreignkey_fields = {'parentnode': RestfulSimplifiedPeriod}

    class ExtjsModelMeta(restfulmetabases.AssignmentExtjsModelMeta):
        """ Metadata for javascript. """

@administrator_restful.register
@extjs_restful_modelapi
@restful_modelapi
class RestfulSimplifiedAssignmentGroup(ModelRestfulView):
    class Meta:
        simplified = SimplifiedAssignmentGroup
        foreignkey_fields = {'parentnode': RestfulSimplifiedAssignment}
        fake_editablefields_formfields = {'fake_examiners': JsonListWithFallbackField(),
                                          'fake_candidates': JsonListWithFallbackField()}

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
