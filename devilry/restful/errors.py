
class InvalidRequestData(Exception):
    def __init__(self, form):
        self.form = form

    def as_dict(self):
        fielderrors = {}
        for k, msgs in self.form.errors.iteritems():
            fielderrors[k] = [msg for msg in msgs]
        return dict(
            nonfield = [e for e in self.form.non_field_errors()],
            field = fielderrors)

    def __str__(self):
        r = []
        d = self.as_dict()
        for msg in d['nonfield']:
            r.append("- %s" % msg)
        for k, msgs in d['field'].iteritems():
            r.append("%s:" % k)
            for msg in msgs:
                r.append("- %s" % msg)
        return str('\n'.join(r))
