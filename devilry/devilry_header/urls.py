from django.urls import re_path
from django.contrib.auth.decorators import login_required

from .views.about_me import AboutMeView
from .views.change_language import ChangeLanguageView

urlpatterns = [
    re_path('^about_me$',
        login_required(AboutMeView.as_view()),
        name='devilry_header_aboutme'),
    re_path('^change_language$',
        login_required(ChangeLanguageView.as_view()),
        name='devilry_change_language'),
]
