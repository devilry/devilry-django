from django import template
import os.path

from django.utils.translation import gettext_lazy

from devilry.devilry_markup import parse_markdown


register = template.Library()


@register.filter("devilry_truncatefileextension")
def devilry_truncatefileextension(value, max_length):
    """
    Args:
        value: filename.
        max_length: number of characters the truncated
            string consists of including the extension

    Returns:
        str: truncated filename.

    Example:
        If max_length is 10, the string "Delivery.pdf" will be
        truncated to "Deli...pdf"
    """
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


@register.filter("devilry_verbosenumber")
def devilry_verbosenumber(value, number):
    """
    Numbers from 1 to 10 is given as verbose(first, second, third, ...)
    and all numbers above 10 has the number and the corresponding ending(11th, 23rd, 32nd, 41st, ...)

    Args:
        value: The value passed(empty in this case).
        number: To get the verbose version of.

    Returns:
        str: Verbose version of number.
    """
    numbers = {
        1: gettext_lazy('first'),
        2: gettext_lazy('second'),
        3: gettext_lazy('third'),
        4: gettext_lazy('fourth'),
        5: gettext_lazy('fifth'),
        6: gettext_lazy('sixth'),
        7: gettext_lazy('seventh'),
        8: gettext_lazy('eighth'),
        9: gettext_lazy('ninth'),
        10: gettext_lazy('tenth')
    }

    if number <= 10:
        # use numbers dictionary
        # to get verbose result
        return numbers[number]
    return '{}.'.format(number)


@register.filter("devilry_group_comment_published")
def devilry_group_comment_published(comment):
    """
    Get the published datetime of a :class:`~devilry_group.GroupComment`

    Args:
        comment: A :obj:`~devilry_group.GroupComment` object.

    Returns:
        DateTime: published datetime of the comment.

    """
    return comment.get_published_datetime()


@register.filter("devilry_group_markdown")
def devilry_group_markdown(value):
    return parse_markdown.markdown_full(value)


@register.inclusion_tag("devilry_group/template_tags/devilry_group_comment_user_is_none.django.html")
def devilry_group_comment_user_is_none():
    return {}
