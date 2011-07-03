from ...restful import restful_modelapi, ModelRestView, RestfulManager
from simplified import SimplifiedNode, SimplifiedSubject, SimplifiedPeriod


__all__ = ('RestfulSimplifiedNode', 'RestfulSimplifiedSubject', 'RestfulSimplifiedPeriod')


administrator_restful = RestfulManager()

@administrator_restful.register
@restful_modelapi
class RestfulSimplifiedNode(ModelRestView):
    class Meta:
        simplified = SimplifiedNode


@administrator_restful.register
@restful_modelapi
class RestfulSimplifiedSubject(ModelRestView):
    class Meta:
        simplified = SimplifiedSubject


@administrator_restful.register
@restful_modelapi
class RestfulSimplifiedPeriod(ModelRestView):
    class Meta:
        simplified = SimplifiedPeriod
