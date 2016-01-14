from django.db.models import Aggregate, Value, IntegerField


class BooleanCount(Aggregate):
    """
    Works just like :class:`django.db.models.Count`, except that the
    aggregated value is cooerced to bool instead of int.
    """
    function = 'COUNT'
    name = 'DevilryBooleanCount'
    template = '%(function)s(%(distinct)s%(expressions)s)'

    def __init__(self, expression, distinct=False, **extra):
        if expression == '*':
            expression = Value(expression)
        super(BooleanCount, self).__init__(
            expression, distinct='DISTINCT ' if distinct else '', output_field=IntegerField(), **extra)

    def __repr__(self):
        return "{}({}, distinct={})".format(
            self.__class__.__name__,
            self.arg_joiner.join(str(arg) for arg in self.source_expressions),
            'False' if self.extra['distinct'] == '' else 'True',
        )

    def convert_value(self, value, expression, connection, context):
        if value is None:
            return False
        return bool(value)
