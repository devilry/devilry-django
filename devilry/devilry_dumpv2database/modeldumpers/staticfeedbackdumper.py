import os

from devilry.apps.core.models import StaticFeedback, StaticFeedbackFileAttachment
from devilry.devilry_dumpv2database import modeldumper


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
                        'relative_file_path': path/to/somefile.py,
                        'size': size of the file(e.g 512 bytes)
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
        return {
            'id': file_attachement.id,
            'filename': file_name,
            'relative_file_path': file_attachement.file.name
        }

    def _get_list_of_attachment_file_info_dicts(self, staticfeedback):
        file_attachment_queryset = staticfeedback.files.all()
        files = {}
        for file_attachement in file_attachment_queryset:
            files[str(file_attachement.id)] = self._get_file_attachement_info_dict(file_attachement)
        return files

    def serialize_model_object(self, obj):
        serialized = super(StaticFeedbackDumper, self).serialize_model_object(obj=obj)
        serialized['fields']['deadline_id'] = obj.delivery.deadline.id
        serialized['fields']['files'] = self._get_list_of_attachment_file_info_dicts(obj)
        return serialized
