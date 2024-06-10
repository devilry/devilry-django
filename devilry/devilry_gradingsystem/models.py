import os
import uuid


# NOTE: Left after removal of FeedbackDraftFile model to avoid migrations breaking
def feedback_draft_file_upload_to(instance, filename):
    extension = os.path.splitext(filename)[1]
    return 'devilry_gradingsystem/feedbackdraftfile/{deliveryid}/{uuid}{extension}'.format(
        deliveryid=instance.delivery_id,
        uuid=str(uuid.uuid1()),
        extension=extension)
