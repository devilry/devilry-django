from django.views.generic import View
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import classonlymethod
from django.conf.urls.defaults import url


class JsAppView(View):
    appname = None
    templatename = 'production'
    with_css = False
    include_old_exjsclasses = False
    libs = []

    @classonlymethod
    def as_appview(cls, appname, **kwargs):
        return cls.as_view(appname=appname, **kwargs)

    def get_base(self, request, **extra):
        kw = {'appname': self.appname,
              'with_css': self.with_css,
              'libs': self.libs,
              'include_old_exjsclasses': self.include_old_exjsclasses}
        kw.update(extra)
        return render(request, 'jsapp/{0}.django.html'.format(self.templatename), kw)

    def get(self, request):
        return self.get_base(request)


class JsAppTestView(JsAppView):
    templatename = 'test'
    def get(self, request):
        return self.get_base(request)


def create_urls(appname, with_css=False, libs=[], include_old_exjsclasses=False):
    kwargs = dict(with_css=with_css, libs=libs, include_old_exjsclasses=include_old_exjsclasses)
    return (url(r'^ui$', login_required(JsAppView.as_appview(appname, **kwargs))),
            url(r'^test$', JsAppView.as_appview(appname, **kwargs)))
