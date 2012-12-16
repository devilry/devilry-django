from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.db import transaction

from .sandbox import Sandbox


class CreateSubjectIntroView(TemplateView):
    template_name = 'devilry_sandbox/createsubject.django.html'

class CreateSubjectCreateView(TemplateView):
    template_name = 'devilry_sandbox/createsubject.django.html'

    def post(self, request):
        with transaction.commit_on_success():
            sandbox = Sandbox()
            subject, num = sandbox.create_autonamed_subject()
            testuser = sandbox.create_user(
                'testuser{num}'.format(num=num),
                'Test User {num}'.format(num=num))
            subject.admins.add(testuser)
            period = sandbox.create_period('approx-spring2013', 'Spring 2013')

            self.request.session['long_name'] = subject.long_name
            self.request.session['username'] = testuser.username
            self.request.session['password'] = testuser.username

        return redirect('devilry-sandbox-createsubject-create')

    def get_context_data(self, **kwargs):
        context = super(CreateSubjectCreateView, self).get_context_data(**kwargs)
        context['success'] = True
        context['long_name'] = self.request.session.pop('long_name')
        context['username'] = self.request.session.pop('username')
        context['password'] = self.request.session.pop('password')
        return context