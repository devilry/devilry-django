from django.urls import path
from django.contrib.auth.decorators import login_required

from cradmin_legacy.apps.cradmin_temporaryfileuploadstore.views.temporary_file_upload_api import (
    UploadTemporaryFilesView,
)

urlpatterns = [
    path(
        "temporary_file_upload_api",
        login_required(UploadTemporaryFilesView.as_view()),
        name="cradmin_temporary_file_upload_api",
    ),
]
