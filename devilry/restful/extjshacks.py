from functools import wraps


def extjshacks(f):
    @wraps(f)
    def wrapper(self, request, *args, **kwargs):
        self.use_extjshacks = bool(request.META.get('HTTP_X_DEVILRY_USE_EXTJS', False))
        return f(self, request, *args, **kwargs)
    return wrapper


def extjswrap(data, use_extjshacks, success=True, total=None):
    """
    If ``use_extjshacks`` is true, wrap ``data`` in the information
    required by extjs.
    """
    if use_extjshacks:
        result = dict(items = data)
        if total != None:
            result['total'] = total
        result['success'] = success
        return result
    else:
        if total == None:
            return data
        else:
            return dict(items=data, total=total)
