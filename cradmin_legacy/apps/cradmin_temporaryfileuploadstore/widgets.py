import json
from xml.sax.saxutils import quoteattr
from django import forms
from django.urls import reverse
from django.template.loader import render_to_string
from django.utils.translation import gettext
from cradmin_legacy.utils import crhumanize


class BulkFileUploadWidget(forms.Widget):
    template_name = "cradmin_legacy/apps/cradmin_temporaryfileuploadstore/bulkfileupload-widget.django.html"

    def __init__(
        self,
        accept=None,
        apiparameters=None,
        dropbox_text=None,
        invalid_filetype_message=None,
        advanced_fileselectbutton_text=None,
        simple_fileselectbutton_text=None,
        autosubmit=False,
        overlaymode_autosubmit_uploading_message=None,
    ):
        """
        Parameters:
            accept (str): Comma separated string of filetypes that we should accept.
                Added to the file upload field as the accept attribute.
                Note that this is not validated serverside - use the accept attribute
                of ``apiparameters`` to do that.
            apiparameters (dict): Dict of API parameters. Here you can
                put values for the ``minutes_to_live``, ``accept``, ``max_filename_length``
                and ``unique_filenames`` attributes of
                :class:`cradmin_legacy.apps.cradmin_temporaryfileuploadstore.models.TemporaryFileCollection`.

                Example::

                    apiparameters = {
                        'minutes_to_live': 10,
                        'accept': 'application/pdf,text/plain,image/*',
                        'unique_filenames': True
                    }
            autosubmit: If this is ``True``, the form is submitted
                when the upload is finished. This also makes it impossible
                to upload more than one batch of files, because the widget
                hides all the upload widgets as soon as any files is added.
                It works with multi-file upload, but the user will only
                be able to upload one batch of files, and they will not
                be able to remove or upload more files.

            overlaymode_autosubmit_uploading_message
                The message to show submitting the form when using overlay mode and autosubmit.

                This is just to ensure that the user understands that the
                request is beeing submitted, and that they should wait and not
                close the browser window.

                Only used if ``autosubmit`` is ``True``, and the form uses the
                form uses ``cradmin-legacy-bulkfileupload-form-overlay="true"``.

        """
        self.accept = accept
        self.apiparameters = apiparameters or {}
        self.dropbox_text = dropbox_text
        self.invalid_filetype_message = invalid_filetype_message
        self.advanced_fileselectbutton_text = advanced_fileselectbutton_text
        self.simple_fileselectbutton_text = simple_fileselectbutton_text
        self.autosubmit = autosubmit
        self.overlaymode_autosubmit_uploading_message = overlaymode_autosubmit_uploading_message

        super().__init__(attrs=None)

    def get_max_filesize_bytes(self):
        max_filesize_bytes = self.apiparameters.get("max_filesize_bytes", None)
        return max_filesize_bytes

    def get_max_filesize_bytes_exceeded_errormessage(self):
        max_filesize_bytes = self.get_max_filesize_bytes()
        if max_filesize_bytes is not None:
            return gettext("Can not upload files larger than %(max_filesize)s.") % {
                "max_filesize": crhumanize.human_readable_filesize(max_filesize_bytes)
            }

    def get_uploadapiurl(self):
        """
        Get the file upload API URL.

        You can override this if you provide your own upload API.
        """
        return reverse("cradmin_temporary_file_upload_api")

    def get_errormessage503(self):
        """
        Get the error message to show on 503 server errors.
        """
        return gettext(
            "Server timeout while uploading the file. This may be caused by a poor upload link and/or a too large file."
        )

    def get_use_singlemode(self):
        """
        If this returns ``True``, only single file upload is allowed.
        Defaults to ``False``, but :class:`.SingleFileUploadWidget`
        overrides this.
        """
        return False

    def get_apiparameters(self):
        """
        Get parameters for the upload API.
        """
        apiparameters = self.apiparameters.copy()
        apiparameters["singlemode"] = self.get_use_singlemode()
        return apiparameters

    def get_angularjs_directive_options(self):
        """
        Get options for the ``cradmin-legacy-bulkfileupload``
        angularjs directive.

        Must return a JSON encodable dict.
        """
        return {
            "uploadapiurl": self.get_uploadapiurl(),
            "apiparameters": self.get_apiparameters(),
            "errormessage503": self.get_errormessage503(),
            "autosubmit": self.autosubmit,
            "close_errormessage_label": gettext("Close"),
            "remove_file_label": gettext("Remove"),
            "removing_file_message": gettext("Removing ..."),
        }

    def __get_rejected_files_errormessage_map(self):
        return {
            "invalid_filetype": str(self.invalid_filetype_message),
            "max_filesize_bytes_exceeded": self.get_max_filesize_bytes_exceeded_errormessage(),
        }

    def get_template_context_data(self, **context):
        """
        Can be overridden to adjust the template context data.
        """
        context["accept"] = self.accept
        context["dropbox_text"] = self.dropbox_text
        context["rejected_files_errormessage_map"] = quoteattr(json.dumps(self.__get_rejected_files_errormessage_map()))
        context["advanced_fileselectbutton_text"] = self.advanced_fileselectbutton_text
        context["simple_fileselectbutton_text"] = self.simple_fileselectbutton_text
        context["angularjs_directive_options"] = quoteattr(json.dumps(self.get_angularjs_directive_options()))
        context["singlemode"] = self.get_use_singlemode()
        context["overlaymode_autosubmit_uploading_message"] = self.overlaymode_autosubmit_uploading_message
        return context

    def render(self, name, value, attrs=None, renderer=None):
        if value is None:
            value = ""
        return render_to_string(
            self.template_name, self.get_template_context_data(hiddenfieldname=name, fieldvalue=value)
        )


class SingleFileUploadWidget(BulkFileUploadWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_use_singlemode(self):
        return True

    def get_template_context_data(self, **context):
        context = super().get_template_context_data(**context)
        return context
