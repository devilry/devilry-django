

class DbSanityCheck(object):
    def __init__(self):
        self.autofixable_errors = []
        self.fatal_errors = []

    def add_autofixable_error(self, msg):
        self.autofixable_errors.append(msg)

    def add_fatal_error(self, msg):
        self.fatal_errors.append(msg)

    def check(self):
        return None

    @classmethod
    def fix(self):
        return None


class DbSanityCheckRegistry(object):
    def __init__(self):
        self.dbsanitychecks = {}

    def register(self, dbsanitycheck):
        self.dbsanitychecks[dbsanitycheck.__name__] = dbsanitycheck
