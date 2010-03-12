class UiMessages(list):
    """ A container for zero or more messages. """

    def add_info(self, msg, raw_html=False):
        self.append(('info_message', raw_html, msg))

    def add_success(self, msg, raw_html=False):
        self.append(('success_message', raw_html, msg))

    def add_warning(self, msg, raw_html=False):
        self.append(('warning_message', raw_html, msg))

    def add_error(self, msg, raw_html=False):
        self.append(('error_message', raw_html, msg))
