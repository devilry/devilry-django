class UiMessages(list):
    """ A container for 0 or more messages. """

    def add_info(self, msg):
        self.append(('info_message', msg))

    def add_warning(self, msg):
        self.append(('info_warning', msg))

    def add_error(self, msg):
        self.append(('info_error', msg))
