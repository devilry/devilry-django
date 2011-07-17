from django.conf.urls.defaults import patterns, url
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView


class JavascriptTemplateView(TemplateView):
    def render_to_response(self, context):
        return super(JavascriptTemplateView, self).render_to_response(context,
                                                              content_type="application/javascript")


urlpatterns = patterns('devilry.apps.gradeeditors',
                       url(r'^approved$',
                           login_required(JavascriptTemplateView.as_view(template_name='gradeeditors/approved.django.js')),
                           name='gradeeditors-approved')
                      )
