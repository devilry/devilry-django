from django.utils.translation import ugettext as _


class UiMessages(list):
    """ A container for zero or more messages. """

    def add_info(self, msg, raw_html=False, title=_("Info"), sticky=False):
        self.append(('info-message', raw_html, msg, title, sticky))

    def add_success(self, msg, raw_html=False, title=_("Success"),
            sticky=False):
        self.append(('success-message', raw_html, msg, title, sticky))

    def add_warning(self, msg, raw_html=False, title=_("Warning"),
            sticky=True):
        self.append(('warning-message', raw_html, msg, title, sticky))

    def add_error(self, msg, raw_html=False, title=_("Error"), sticky=True):
        self.append(('error-message', raw_html, msg, title, sticky))

    def save(self, request):
        request.session['uimessages'] = self

    def load(self, request):
        messages = request.session.get('uimessages')
        if messages:
            for m in messages:
                self.append(m)
            del request.session['uimessages']
