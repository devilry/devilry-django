from devilry.restful import restful_modelapi, ModelRestfulView, RestfulManager
from devilry.apps.extjshelpers import extjs_restful_modelapi
from devilry.apps.administrator.restful import (RestfulSimplifiedAssignment,
                                                RestfulSimplifiedDelivery)
from ..simplified.administrator import (SimplifiedConfig,
                                        SimplifiedFeedbackDraft)
from examiner import RestfulSimplifiedFeedbackDraftCommon


__all__ = ('RestfulSimplifiedConfig', 'RestfulSimplifiedFeedbackDraft')
administrator_restful = RestfulManager()

@administrator_restful.register
@extjs_restful_modelapi
@restful_modelapi
class RestfulSimplifiedConfig(ModelRestfulView):
    class Meta:
        simplified = SimplifiedConfig
        belongs_to = RestfulSimplifiedAssignment


@administrator_restful.register
@extjs_restful_modelapi
@restful_modelapi
class RestfulSimplifiedFeedbackDraft(RestfulSimplifiedFeedbackDraftCommon, ModelRestfulView):
    class Meta:
        simplified = SimplifiedFeedbackDraft
        belongs_to = RestfulSimplifiedDelivery
