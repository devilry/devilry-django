from django.conf.urls import url, patterns
from django.conf import settings
from django_cradmin.apps.cradmin_resetpassword.views.begin import BeginPasswordResetView
from django_cradmin.apps.cradmin_resetpassword.views.email_sent import EmailSentView
from django_cradmin.apps.cradmin_resetpassword.views.reset import ResetPasswordView


# For now, this can only be triggered from the django_cradmin EmailLoginForm.
# That makes the EmailAuthBackend a requirement for having password-reset
if getattr(settings, 'DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND', False) \
        and getattr(settings, 'DJANGO_CRADMIN_FORGOTPASSWORD_URL', None) is not None:
    urlpatterns = patterns(
        '',
        url(r'^begin',
            BeginPasswordResetView.as_view(),
            name="cradmin-resetpassword-begin"),
        url(r'^email-sent',
            EmailSentView.as_view(),
            name="cradmin-resetpassword-email-sent"),
        url(r'^reset/(?P<token>.+)',
            ResetPasswordView.as_view(),
            name="cradmin-resetpassword-reset"),
    )
else:
    urlpatterns = []