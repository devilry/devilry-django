from ...restful import restful_modelapi, ModelRestfulView, RestfulManager
from simplified import (SimplifiedSubject, SimplifiedPeriod,
                        SimplifiedAssignment, SimplifiedAssignmentGroup,
                        SimplifiedDelivery, SimplifiedDeadline,
                        SimplifiedStaticFeedback, SimplifiedFileMeta)


__all__ = ('RestfulSimplifiedSubject',
           'RestfulSimplifiedPeriod', 'RestfulSimplifiedAssignment',
           'RestfulSimplifiedAssignmentGroup', 'RestfulSimplifiedDelivery',
           'RestfulSimplifiedDeadline', 'RestfulSimplifiedFileMeta',
           'RestfulStaticFeedback')


student_restful = RestfulManager()


@student_restful.register
@restful_modelapi
class RestfulSimplifiedSubject(ModelRestfulView):
    class Meta:
        simplified = SimplifiedSubject


@student_restful.register
@restful_modelapi
class RestfulSimplifiedPeriod(ModelRestfulView):
    class Meta:
        simplified = SimplifiedPeriod
        foreignkey_fields = {'parentnode': RestfulSimplifiedSubject}


@student_restful.register
@restful_modelapi
class RestfulSimplifiedAssignment(ModelRestfulView):
    class Meta:
        simplified = SimplifiedAssignment
        foreignkey_fields = {'parentnode': RestfulSimplifiedPeriod}


@student_restful.register
@restful_modelapi
class RestfulSimplifiedAssignmentGroup(ModelRestfulView):
    class Meta:
        simplified = SimplifiedAssignmentGroup
        foreignkey_fields = {'parentnode': RestfulSimplifiedAssignment}


@student_restful.register
@restful_modelapi
class RestfulSimplifiedDelivery(ModelRestfulView):
    class Meta:
        simplified = SimplifiedDelivery
        foreignkey_fields = {'parentnode': RestfulSimplifiedAssignmentGroup}


@student_restful.register
@restful_modelapi
class RestfulSimplifiedDeadline(ModelRestfulView):
    class Meta:
        simplified = SimplifiedDeadline
        foreignkey_fields = {'parentnode': RestfulSimplifiedAssignmentGroup}


@student_restful.register
@restful_modelapi
class RestfulSimplifiedStaticFeedback(ModelRestfulView):
    class Meta:
        simplified = SimplifiedStaticFeedback
        foreignkey_fields = {'parentnode': RestfulSimplifiedDelivery}


@student_restful.register
@restful_modelapi
class RestfulSimplifiedFileMeta(ModelRestfulView):
    class Meta:
        simplified = SimplifiedFileMeta
        foreignkey_fields = {'parentnode': RestfulSimplifiedDelivery}
