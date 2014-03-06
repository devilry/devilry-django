from django import template
import calendar

register = template.Library()

@register.tag(name="devilry_calendar")
def do_calendar_events(parser, token):
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, format_string = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires a single argument" % token.contents.split()[0])
    if not (format_string[0] == format_string[-1] and format_string[0] in ('"', "'")):
        raise template.TemplateSyntaxError("%r tag's argument should be in quotes" % tag_name)
    return CalendarEventsNode(format_string[1:-1])


class CalendarEventsNode(template.Node):
    """docstring for CalendarEventsNode"""
    def __init__(self, format_string):
        super(CalendarEventsNode, self).__init__()
        self.format_string = format_string
        self.devilry_calendar = calendar.HTMLCalendar()
        print format_string
    
    def render(self, context):
        return self.devilry_calendar.formatmonth(2014,3)