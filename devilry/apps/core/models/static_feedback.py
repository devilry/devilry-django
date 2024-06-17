import os
import uuid


# NOTE: Left after removal of StaticFeedback model to avoid migrations breaking
def staticfeedback_fileattachment_upload_to(instance, filename):
    extension = os.path.splitext(filename)[1]
    return 'devilry_core/staticfeedbackfileattachment/{staticfeedback_id}/{uuid}{extension}'.format(
        staticfeedback_id=instance.staticfeedback_id,
        uuid=str(uuid.uuid1()),
        extension=extension)
