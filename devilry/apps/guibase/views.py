from django.views.generic import View
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import classonlymethod
from django.conf.urls.defaults import url


class GuiBaseView(View):
    appname = None
    templatename = None
    with_css = False
    include_old_exjsclasses = False
    libs = []

    @classonlymethod
    def as_appview(cls, appname, templatename, **kwargs):
        return cls.as_view(appname=appname, templatename=templatename, **kwargs)

    def get(self, request):
        return render(request, 'guibase/{0}.django.html'.format(self.templatename),
                      {'appname': self.appname,
                       'with_css': self.with_css,
                       'libs': self.libs,
                       'include_old_exjsclasses': self.include_old_exjsclasses})



def create_urls(appname, with_css=False, libs=[], include_old_exjsclasses=False):
    kwargs = dict(with_css=with_css, libs=libs, include_old_exjsclasses=include_old_exjsclasses)
    return (url(r'^ui$', login_required(GuiBaseView.as_appview(appname, 'production', **kwargs))),
            url(r'^test$', GuiBaseView.as_appview(appname, 'test', **kwargs)))
