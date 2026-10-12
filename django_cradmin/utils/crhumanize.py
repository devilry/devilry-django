from builtins import str


def human_readable_filesize(size_in_bytes):
    """
    Humanize the given file size in bytes.

    Returns a number suffixed with ``B``, ``KB``, ``MB``,
    ``GB`` or ``TB``.

    Examples:

        >>> from django_cradmin.utils import crhumanize
        >>> crhumanize.human_readable_filesize(1)
        '1B'
        >>> crhumanize.human_readable_filesize(2344234345)
        '2.34GB'
        >>> crhumanize.human_readable_filesize(23442343451234)
        '23.44TB'
    """
    if size_in_bytes < 1000:
        return "{}B".format(size_in_bytes)
    if size_in_bytes < 1000000:
        return "{}KB".format(int(size_in_bytes / 1000.0))
    elif size_in_bytes < 1000000000:
        return "{:.1f}MB".format(size_in_bytes / 1000000.0)
    elif size_in_bytes < 1000000000000:
        return "{:.2f}GB".format(size_in_bytes / 1000000000.0)
    else:
        return "{:.2f}TB".format(size_in_bytes / 1000000000000.0)


def dehumanize_readable_filesize(humanized_size):
    """
    Does the opposite of :func:`.human_readable_filesize`.

    Takes a string containing a number suffixed with ``B``, ``KB``, ``MB``,
    ``GB`` or ``TB``, and returns an int with the number of bytes.

    Examples:

        >>> from django_cradmin.utils import crhumanize
        >>> crhumanize.dehumanize_readable_filesize('999B')
        999
        >>> crhumanize.dehumanize_readable_filesize('2.34GB')
        2340000000
        >>> crhumanize.dehumanize_readable_filesize('43.312TB')
        43312000000000
    """
    if not isinstance(humanized_size, str):
        raise ValueError("humanized_size must be a string (unicode in python 2)")
    humanized_size = humanized_size[:-1]
    if humanized_size[-1].isdigit():
        return int(humanized_size)
    else:
        sizechar = humanized_size[-1]
        number = float(humanized_size[:-1])
        multiply_by = {"K": 1000, "M": 1000000, "G": 1000000000, "T": 1000000000000}[sizechar]
        return int(number * multiply_by)
