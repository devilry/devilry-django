from cradmin_legacy.crispylayouts import CradminSubmitButton


class BulkFileUploadSubmit(CradminSubmitButton):
    template = "cradmin_legacy/apps/cradmin_temporaryfileuploadstore/bulkfileupload-submit.django.html"
    extra_button_attributes = {"cradmin-legacy-bulkfileupload-submit": ""}

    def __init__(self, name, value, uploading_text=None, uploading_icon_cssclass=None, **kwargs):
        self.uploading_text = uploading_text or value
        self.uploading_icon_cssclass = uploading_icon_cssclass
        super().__init__(name, value, **kwargs)
