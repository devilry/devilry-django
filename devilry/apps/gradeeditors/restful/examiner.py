from devilry.restful import restful_modelapi, ModelRestfulView, RestfulManager
from devilry.apps.extjshelpers import extjs_restful_modelapi
from devilry.apps.examiner.restful import (RestfulSimplifiedAssignment,
                                           RestfulSimplifiedDelivery)
from ..simplified.examiner import (SimplifiedConfig,
                                   SimplifiedFeedbackDraft)


examiner_restful = RestfulManager()

@examiner_restful.register
@extjs_restful_modelapi
@restful_modelapi
class RestfulSimplifiedConfig(ModelRestfulView):
    class Meta:
        simplified = SimplifiedConfig
        foreignkey_fields = {'assignment': RestfulSimplifiedAssignment}


@examiner_restful.register
@extjs_restful_modelapi
@restful_modelapi
class RestfulSimplifiedFeedbackDraft(ModelRestfulView):
    class Meta:
        simplified = SimplifiedFeedbackDraft
        foreignkey_fields = {'delivery': RestfulSimplifiedDelivery}
