from django import template
import os.path
register = template.Library()

@register.filter("devilry_truncatefileext")
def devilry_truncatefileext(value, max_length):
    # Filter that takes a filename-string and
    # and gets the n first characters from the string
    # and combines it with the extension of the file.
    # Example: if max_length is 3, then "SomeFile.pdf" becomes "Som...pdf".
    if len(value) > max_length:
        extension = os.path.splitext(value)[1]
        truncated_value = value[:max_length] + '..' + extension
        return truncated_value
    return value