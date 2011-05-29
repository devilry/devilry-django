from django import template


register = template.Library()

@register.filter
def iter_actionregistry(registry, item):
    return registry.itervalues(item)
