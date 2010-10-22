

class DbSanityCheck(object):
    def __init__(self):
        self.autofixable_errors = []
        self.fatal_errors = []
        self.check()

    @classmethod
    def get_key(cls):
        return "%s.%s" % (cls.__module__, cls.__name__)

    @classmethod
    def get_label(cls):
        return cls.__name__

    def add_autofixable_error(self, msg):
        self.autofixable_errors.append(msg)

    def add_fatal_error(self, msg):
        self.fatal_errors.append(msg)

    def is_ok(self):
        return not self.autofixable_errors and not self.fatal_errors

    def check(self):
        pass

    @classmethod
    def fix(cls):
        pass



class DbSanityCheckRegistry(object):
    def __init__(self):
        self.dbsanitychecks = {}

    def register(self, dbsanitycheck):
        self.dbsanitychecks[dbsanitycheck.get_key()] = dbsanitycheck

    def iterchecks(self):
        for key, cls in self.dbsanitychecks.iteritems():
            yield key, cls()

    def iterfix(self):
        for key, cls in self.dbsanitychecks.iteritems():
            cls.fix()
            yield key, cls

    def __getitem__(self, key):
        return self.dbsanitychecks[key]

    def iterkeys(self):
        return self.dbsanitychecks.iterkeys()


dbsanity_registry = DbSanityCheckRegistry()
