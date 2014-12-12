from devilry.apps.core.models import Node


def _get_by_path_kw(pathlist):
    """ Used by :meth:`get_by_path` to create the required kwargs for
    Node.objects.get(). Might be a starting point for more sophisticated
    queries including paths. Example::

        ifi = Node.objects.get(**Node._get_by_path_kw(['uio', 'ifi']))

    :param pathlist: A list of node-names, like ``['uio', 'ifi']``.
    """
    kw = {}
    key = 'short_name'
    for short_name in reversed(pathlist):
        kw[key] = short_name
        key = 'parentnode__' + key
    return kw

def get_by_path(path):
    """ Get a node by path.

    Raises :exc:`Node.DoesNotExist` if the query does not match.
    
    :param path: The path to a Node, like ``'uio.ifi'``.
    :type path: str
    :return: A Node-object.
    """
    return Node.objects.get(**_get_by_path_kw(path.split('.')))
