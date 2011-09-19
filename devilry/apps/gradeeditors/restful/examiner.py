from datetime import datetime
from devilry.restful import restful_modelapi, ModelRestfulView, RestfulManager
from devilry.apps.extjshelpers import extjs_restful_modelapi
from devilry.apps.examiner.restful import (RestfulSimplifiedAssignment,
                                           RestfulSimplifiedDelivery)
from ..simplified.examiner import (SimplifiedConfig,
                                   SimplifiedFeedbackDraft)
from ..models import FeedbackDraft


__all__ = ('RestfulSimplifiedConfig', 'RestfulSimplifiedFeedbackDraft')
examiner_restful = RestfulManager()

@examiner_restful.register
@extjs_restful_modelapi
@restful_modelapi
class RestfulSimplifiedConfig(ModelRestfulView):
    class Meta:
        simplified = SimplifiedConfig
        foreignkey_fields = {'assignment': RestfulSimplifiedAssignment}


class RestfulSimplifiedFeedbackDraftCommon(object):
    def extra_create_or_replace_responsedata(self, obj_id):
        draft = FeedbackDraft.objects.get(id=obj_id)
        staticfeedback = draft.to_staticfeedback()
        return dict(rendered_view = staticfeedback.rendered_view,
                    save_timestamp = datetime.now(), # This is used for previews, so a preview of how a date will look makes sense.
                    grade = staticfeedback.grade,
                    points = staticfeedback.points,
                    is_passing_grade = staticfeedback.is_passing_grade)


@examiner_restful.register
@extjs_restful_modelapi
@restful_modelapi
class RestfulSimplifiedFeedbackDraft(RestfulSimplifiedFeedbackDraftCommon, ModelRestfulView):
    class Meta:
        simplified = SimplifiedFeedbackDraft
        foreignkey_fields = {'delivery': RestfulSimplifiedDelivery}
