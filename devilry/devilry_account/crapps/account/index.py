from django.utils import translation, timezone
from django.conf import settings
from django.views.generic import TemplateView

from devilry.apps.core.models import RelatedExaminer, RelatedStudent
from devilry.devilry_account.crapps.account import utils


class IndexView(TemplateView):
    template_name = 'devilry_account/crapps/account/index.django.html'

    def get_related_examiners_for_active_periods(self):
        now = timezone.now()
        return RelatedExaminer.objects \
            .select_related('user', 'period', 'period__parentnode') \
            .filter(
                active=True,
                user=self.request.user,
                period__start_time__lte=now, period__end_time__gt=now
            ).order_by('period__parentnode__long_name')
    
    def get_related_students_for_active_periods(self):
        now = timezone.now()
        return RelatedStudent.objects \
            .select_related('user', 'period', 'period__parentnode') \
            .filter(
                active=True,
                user=self.request.user,
                period__start_time__lte=now, period__end_time__gt=now
            ).order_by('period__parentnode__long_name')

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['email_auth_backend'] = settings.CRADMIN_LEGACY_USE_EMAIL_AUTH_BACKEND
        context['useremails'] = list(self.request.user.useremail_set.all())
        context['useremail_count'] = len(context['useremails'])
        context['usernames'] = list(self.request.user.username_set.all())
        context['username_count'] = len(context['usernames'])
        languagecode = translation.get_language()
        context['language_code'] = languagecode
        context['language_name'] = utils.get_language_name(languagecode=languagecode)
        context['related_examiners_for_active_periods'] = self.get_related_examiners_for_active_periods()
        context['related_students_for_active_periods'] = self.get_related_students_for_active_periods()
        return context
