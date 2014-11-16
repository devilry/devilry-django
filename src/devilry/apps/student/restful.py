from devilry.restful import restful_modelapi, ModelRestfulView, RestfulManager
from devilry.apps.extjshelpers import extjs_restful_modelapi
from simplified import (SimplifiedSubject, SimplifiedPeriod,
                        SimplifiedAssignment, SimplifiedAssignmentGroup,
                        SimplifiedDelivery, SimplifiedDeadline,
                        SimplifiedStaticFeedback, SimplifiedFileMeta, SimplifiedRelatedStudentKeyValue)
from devilry.coreutils.restful.metabases import (DeadlineExtjsModelMeta,
                                                 AssignmentGroupExtjsModelMeta,
                                                 DeliveryExtjsModelMeta,
                                                 AssignmentExtjsModelMeta) 

__all__ = ('RestfulSimplifiedSubject',
           'RestfulSimplifiedPeriod', 'RestfulSimplifiedAssignment',
           'RestfulSimplifiedAssignmentGroup', 'RestfulSimplifiedDelivery',
           'RestfulSimplifiedDeadline', 'RestfulSimplifiedFileMeta',
           'RestfulSimplifiedStaticFeedback', 'RestfulSimplifiedRelatedStudentKeyValue')


student_restful = RestfulManager()


@student_restful.register
@extjs_restful_modelapi
@restful_modelapi
class RestfulSimplifiedSubject(ModelRestfulView):
    class Meta:
        simplified = SimplifiedSubject


@student_restful.register
@extjs_restful_modelapi
@restful_modelapi
class RestfulSimplifiedPeriod(ModelRestfulView):
    class Meta:
        simplified = SimplifiedPeriod
        belongs_to = RestfulSimplifiedSubject

@student_restful.register
@extjs_restful_modelapi
@restful_modelapi
class RestfulSimplifiedRelatedStudentKeyValue(ModelRestfulView):
    class Meta:
        simplified = SimplifiedRelatedStudentKeyValue


@student_restful.register
@extjs_restful_modelapi
@restful_modelapi
class RestfulSimplifiedAssignment(ModelRestfulView):
    class Meta:
        simplified = SimplifiedAssignment
        belongs_to = RestfulSimplifiedPeriod

    class ExtjsModelMeta(AssignmentExtjsModelMeta):
        """ Extjs model meta """


@student_restful.register
@extjs_restful_modelapi
@restful_modelapi
class RestfulSimplifiedAssignmentGroup(ModelRestfulView):
    class Meta:
        simplified = SimplifiedAssignmentGroup
        belongs_to = RestfulSimplifiedAssignment

    class ExtjsModelMeta(AssignmentGroupExtjsModelMeta):
        """ Meta for Extjs """


@student_restful.register
@extjs_restful_modelapi
@restful_modelapi
class RestfulSimplifiedDelivery(ModelRestfulView):
    class Meta:
        simplified = SimplifiedDelivery
        belongs_to = RestfulSimplifiedAssignmentGroup

    class ExtjsModelMeta(DeliveryExtjsModelMeta):
        """ Meta for Extjs """

@student_restful.register
@extjs_restful_modelapi
@restful_modelapi
class RestfulSimplifiedDeadline(ModelRestfulView):
    class Meta:
        simplified = SimplifiedDeadline
        belongs_to = RestfulSimplifiedAssignmentGroup

    class ExtjsModelMeta(DeadlineExtjsModelMeta):
        """ Metadata for Extjs """


@student_restful.register
@extjs_restful_modelapi
@restful_modelapi
class RestfulSimplifiedStaticFeedback(ModelRestfulView):
    class Meta:
        simplified = SimplifiedStaticFeedback
        belongs_to = RestfulSimplifiedDelivery


@student_restful.register
@extjs_restful_modelapi
@restful_modelapi
class RestfulSimplifiedFileMeta(ModelRestfulView):
    class Meta:
        simplified = SimplifiedFileMeta
        belongs_to = RestfulSimplifiedDelivery
