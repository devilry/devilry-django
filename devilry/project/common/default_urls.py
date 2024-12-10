from cradmin_legacy.apps.cradmin_temporaryfileuploadstore.views.temporary_file_upload_api import (
    UploadTemporaryFilesView,
)
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import include, path

from devilry.devilry_comment.views import markdown_help
from devilry.devilry_frontpage import crinstance_frontpage
from devilry.project.common.http_error_handlers import *
from devilry.utils.csrfutils import csrf_exempt_if_configured  # noqa

admin.site.login = login_required(admin.site.login)


devilry_urls = [
    path(
        "cradmin_temporaryfileuploadstore/temporary_file_upload_api",
        login_required(csrf_exempt_if_configured(UploadTemporaryFilesView.as_view())),
        name="cradmin_temporary_file_upload_api",
    ),
    path("markup/", include("devilry.devilry_markup.urls")),
    path("authenticate/", include("devilry.devilry_authenticate.urls")),
    path("devilry_resetpassword/", include("devilry.devilry_resetpassword.urls")),
    path(
        "cradmin_temporaryfileuploadstore/",
        include("cradmin_legacy.apps.cradmin_temporaryfileuploadstore.urls"),
    ),
    path("account/", include("devilry.devilry_account.urls")),
    path("devilry_help/", include("devilry.devilry_help.urls")),
    path("devilry_core/", include("devilry.apps.core.urls")),
    path("devilry_settings/", include("devilry.devilry_settings.urls")),
    path("devilry_student/", include("devilry.devilry_student.urls")),
    path("devilry_group/", include("devilry.devilry_group.urls")),
    path("devilry_gradeform/", include("devilry.devilry_gradeform.urls")),
    path("devilry_admin/", include("devilry.devilry_admin.urls")),
    path("djangoadmin/", admin.site.urls),
    path("devilry_header/", include("devilry.devilry_header.urls")),
    path("devilry_bulkcreate_users/", include("devilry.devilry_bulkcreate_users.urls")),
    path("devilry_examiner/", include("devilry.devilry_examiner.urls")),
    path("devilry_statistics/", include("devilry.devilry_statistics.urls")),
    path("devilry_comment/", include("devilry.devilry_comment.urls")),
    path("markdown-help", markdown_help.MarkdownHelpView.as_view()),
    path("", include(crinstance_frontpage.CrAdminInstance.urls())),
]
