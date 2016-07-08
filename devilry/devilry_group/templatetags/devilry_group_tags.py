from django import template
import os.path
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
        1: 'first', 2: 'second', 3: 'third', 4: 'fourth', 5: 'fifth',
        6: 'sixth', 7: 'seventh', 8: 'eighth', 9: 'ninth', 10: 'tenth'
    }

    def last_digit(num):
        # returns the last or two last numbers.
        n = str(num)
        if n[len(n)-2] is '1':
            # return the last two digits if number is
            # from 11 to 19 to get th-ending.
            return int(n[len(n)-1]+n[len(n)-2])
        return int(n[len(n)-1])

    if number <= 10:
        # use numbers dictionary
        # to get verbose result
        return numbers[number]
    elif number <= 19:
        # all numbers between 10 and 20 ends with th.
        return str(number)+'th'
    else:
        # handle numbers over 19
        n = last_digit(number)
        if n > 3 or n == 0:
            return str(number)+'th'
        return {
            1: str(number)+'st',
            2: str(number)+'nd',
            3: str(number)+'rd',
        }[n]


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
