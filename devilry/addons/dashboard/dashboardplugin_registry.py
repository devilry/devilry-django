from django.conf import settings

class PluginItem(object):

    def __init__(self, key, label, url, description, iconurl, student_access, examiner_access, admin_access):
        self.key = key
        self.label = label
        self.url = settings.DEVILRY_MAIN_PAGE + url
        self.icon = key + ".png"
        self.description = description
        self.student_access = student_access
        self.examiner_access = examiner_access
        self.admin_access = admin_access
    
    def can_show(self, student, examiner, admin):
        return (self.student_access and student) or (self.examiner_access and examiner) or (self.admin_access and admin)


_registry = {}

def register(key, label, url, description, icon=None, student_access=False, examiner_access=False, admin_access=False):
    r = PluginItem(key, label, url, description, icon, student_access, examiner_access, admin_access)
    #print "%s %s %s %s %s" % (key, label, url, icon, description)
    _registry[r.key] = r


def get(key):
    return _registry[key]

def values():
    values = _registry.values()

def iter_values(student=False, examiner=False, admin=False):
    for value in _registry.itervalues():
        if value.can_show(student, examiner, admin):
            yield (value)


