from ...restful import restful_modelapi, ModelRestView
from simplified import SimplifiedNode, SimplifiedSubject, SimplifiedPeriod


__all__ = ('RestfulSimplifiedNode', 'RestfulSimplifiedSubject', 'RestfulSimplifiedPeriod')


@restful_modelapi
class RestfulSimplifiedNode(ModelRestView):
    class Meta:
        simplified = SimplifiedNode


@restful_modelapi
class RestfulSimplifiedSubject(ModelRestView):
    class Meta:
        simplified = SimplifiedSubject


@restful_modelapi
class RestfulSimplifiedPeriod(ModelRestView):
    class Meta:
        simplified = SimplifiedPeriod
