from ...restful import restful_modelapi, ModelRestfulView, RestfulManager
from simplified import SimplifiedNode, SimplifiedSubject, SimplifiedPeriod


__all__ = ('RestfulSimplifiedNode', 'RestfulSimplifiedSubject', 'RestfulSimplifiedPeriod')


administrator_restful = RestfulManager()

@administrator_restful.register
@restful_modelapi
class RestfulSimplifiedNode(ModelRestfulView):
    class Meta:
        simplified = SimplifiedNode


@administrator_restful.register
@restful_modelapi
class RestfulSimplifiedSubject(ModelRestfulView):
    class Meta:
        simplified = SimplifiedSubject


@administrator_restful.register
@restful_modelapi
class RestfulSimplifiedPeriod(ModelRestfulView):
    class Meta:
        simplified = SimplifiedPeriod
