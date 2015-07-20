from django import template
import os.path
register = template.Library()

@register.filter("devilry_truncatefileextension")
def devilry_truncatefileextension(value, max_length):
    # max_length is the number of characters the truncated
    # string consists of including the extension
    # Example:  if max_length is 10, the string "Delivery.pdf" will be
    #           truncated to "Deli...pdf"
    # Three letters from the filename will be showed either way.
    if len(value) == 0:
        return 'NO_NAME'
    else:
        offset = 3              # show at least three letters from filename
        min_value_length = 8    # entire value name is same length or less than ex. Del.html

        if len(value) <= min_value_length:
            return value
        elif len(value) > max_length:
            splitted = os.path.splitext(value)
            value_extension = splitted[1].strip('.')   # get extension

            if (max_length - len(value_extension) - 3) < offset:
                # show at least three letters from valuename
                # to ensure no files are called "...<fileextension>"
                truncated_value = value[:offset] + '...' + value_extension
            else:
                truncated_value = value[:max_length - len(value_extension) - 3] + '...' + value_extension
            return truncated_value

    return value