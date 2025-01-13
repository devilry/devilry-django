# -*- coding: utf-8 -*-

# django imports
from django.contrib.auth.decorators import login_required
from django.urls import include, path

# devilry imports
from devilry.devilry_group.cradmin_instances import crinstance_admin, crinstance_examiner, crinstance_student
from devilry.devilry_group.views.redirects import RedirectToFeedbackAsAdminOrExaminerView

urlpatterns = [
    path("student/", include(crinstance_student.StudentCrInstance.urls())),
    path("examiner/", include(crinstance_examiner.ExaminerCrInstance.urls())),
    path("admin/", include(crinstance_admin.AdminCrInstance.urls())),
    path(
        "redirect/feedbackfeed_as_examiner_or_admin/<int:assignment_group_id>",
        login_required(RedirectToFeedbackAsAdminOrExaminerView.as_view()),
        name="devilry_group_redirect_to_feedback_as_admin_or_examiner",
    ),
]
