from django import template

register = template.Library()

@register.filter(name='status')
def status(value, arg):
    print value, arg
    return "HEI"
