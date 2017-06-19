import os
import mimetypes

from devilry.devilry_dumpv2database import modeldumper
from devilry.apps.core.models import StaticFeedback, StaticFeedbackFileAttachment


class StaticFeedbackDumper(modeldumper.ModelDumper):
    """
    Dumps a StaticFeedback to file. This also includes meta info about the file belonging to the feedback
    (StaticFeedbackFileAttachments).

    The dictionary created looks like this without files::
        {
            StaticFeedback meta data...,
            fields: {
                StaticFeedback attributes...,
                files: []
            }
        }

    And with files::
        {
            StaticFeedback meta data...,
            fields: {
                StaticFeedback attributes...,
                files: [
                    {
                        'filename': 'somefile.py',
                        'absolute_file_path': absolute/path/to/somefile.py,
                        'size': size of the file(e.g 512 bytes),
                        'mimetype': 'text/x-python'
                    },
                    ...
                ]
            }
        }
    """
    def get_model_class(self):
        return StaticFeedback

    def _get_file_attachement_info_dict(self, file_attachement):
        file_name = file_attachement.filename
        abs_path = os.path.abspath(file_attachement.file.file.name)
        return {
            'filename': file_name,
            'absolute_file_path': abs_path,
            'size': os.stat(abs_path).st_size,
            'mimetype': mimetypes.guess_type(file_name)[0]
        }

    def _get_list_of_attachment_file_info_dicts(self, file_attachment_queryset):
        if file_attachment_queryset.count() == 0:
            return []
        file_list = [self._get_file_attachement_info_dict(file_attachement)
                     for file_attachement in file_attachment_queryset]
        return file_list

    def serialize_model_object(self, obj):
        serialized = super(StaticFeedbackDumper, self).serialize_model_object(obj=obj)
        serialized['fields']['deadline_id'] = obj.delivery.deadline.id
        serialized['fields']['files'] = [] # self._get_list_of_attachment_file_info_dicts(obj.files.all())
        #TODO TEMPORARILY DISABLE FILES
        return serialized
