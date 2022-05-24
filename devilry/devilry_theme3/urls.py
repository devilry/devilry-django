from django.urls import path

from .views import WcagDebugView

urlpatterns = [
    path('wcag-debug', WcagDebugView.as_view()),
]
