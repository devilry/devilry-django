def truncate_filename(filename, length):
    """
    >>> truncate_filename("hello-cruel-world.txt", 12) #doctest:-ELLIPSIS
    'hello....txt'
    >>> truncate_filename("hello-cruel-world.txt", 20) #doctest:-ELLIPSIS
    'hello-cru...orld.txt'
    >>> truncate_filename("hello-cruel-world.txt", 21) #doctest:-ELLIPSIS
    'hello-cruel-world.txt'
    """
    if len(filename) > length:
        center = len(filename) / 2
        diff = length/2
        a, b = filename[0:diff-1], filename[len(filename)-diff+2:]
        #return filename[:length-3] + "..."
        return a + "..." + b
    else:
        return filename
