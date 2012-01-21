from django.views.generic import View
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import classonlymethod


class GuiBaseView(View):
    appname = None

    @classonlymethod
    def as_appview(cls, appname):
        return login_required(cls.as_view(appname=appname))

    def get(self, request):
        return render(request, 'guibase.django.html', {'appname': self.appname})
