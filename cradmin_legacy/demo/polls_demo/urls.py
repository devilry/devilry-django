from django.urls import path, include

from cradmin_legacy.demo.polls_demo import cradmin
from .views import poll_views

urlpatterns = [
    path("", poll_views.IndexView.as_view(), name="index"),
    path("<int:pk>/", poll_views.DetailView.as_view(), name="detail"),
    path("<int:pk>/results/", poll_views.ResultsView.as_view(), name="results"),
    path("<int:question_id>/vote/", poll_views.vote, name="vote"),
    path("cradmin/", include(cradmin.CrAdminInstance.urls()), name="cradmin"),
]
