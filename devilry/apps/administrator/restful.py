from ...restful import restful_modelapi, ModelRestfulView, RestfulManager
from simplified import SimplifiedNode, SimplifiedSubject, SimplifiedPeriod


__all__ = ('RestfulSimplifiedNode', 'RestfulSimplifiedSubject', 'RestfulSimplifiedPeriod')


administrator_restful = RestfulManager()

@administrator_restful.register
@restful_modelapi
class RestfulSimplifiedNode(ModelRestfulView):
    class Meta:
        simplified = SimplifiedNode
        #foreignkey_fields = {'parentnode__id': RestfulSimplifiedNode}


@administrator_restful.register
@restful_modelapi
class RestfulSimplifiedSubject(ModelRestfulView):
    class Meta:
        simplified = SimplifiedSubject
        foreignkey_fields = {'parentnode__id': RestfulSimplifiedNode}


@administrator_restful.register
@restful_modelapi
class RestfulSimplifiedPeriod(ModelRestfulView):
    class Meta:
        simplified = SimplifiedPeriod
        foreignkey_fields = {'parentnode__id': RestfulSimplifiedSubject}
