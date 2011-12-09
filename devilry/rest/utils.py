import inspect
import re
from devilry.rest.error import InvalidParameterTypeError

def subdict(dct, *keys):
    return dict((key, dct[key]) for key in keys)


def todict(obj, *attrs):
    return dict((attr, getattr(obj, attr)) for attr in attrs)



def force_paramtypes(**params):
    def check_types(func, params = params):
        def modified(*args, **kw):
            argspec = inspect.getargspec(func)
            kw.update(zip(argspec.args, args))
            for name, type in params.iteritems():
                param = kw.get(name)
                if param == None:
                    continue
                elif not isinstance(param, type):
                    try:
                        kw[name] = type(param)
                    except:
                        raise InvalidParameterTypeError("Parameter '{0}' should be type '{1}'".format(name, type.__name__))
            return func(**kw)
        return modified
    return check_types


class MediaRange(object):
    def __init__(self, ttype, subtype, quality):
        self.ttype = ttype
        self.subtype = subtype
        self.wildcardcount = 0
        if ttype == '*':
            self.wildcardcount += 1
        if subtype == '*':
            self.wildcardcount += 1
        if quality == '':
            self.quality = 1
        else:
            self.quality = float(quality)

    def __cmp__(self, other):
        comp = cmp(other.quality, self.quality) # We want descending order
        if comp == 0:
            return cmp(self.wildcardcount, other.wildcardcount) # Less wildcards means higher precedence (*/* is worst)
        else:
            return comp

    def match(self, ttype, subtype):
        return self._typematch(self.ttype, ttype) and self._typematch(self.subtype, subtype)

    def _typematch(self, patt, ttype):
        return patt == '*' or patt == ttype

    def __str__(self):
        return '{ttype}/{subtype};q={quality}'.format(**self.__dict__)

class HttpAccessHeaderParser(object):
    """
    Parser for HTTP Accept header: http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html
    """
    nonpatt_type_regex = '[a-zA-Z0-9_+-]+'
    type_regex = '(?:{nonpatt_type_regex}|\*)'.format(nonpatt_type_regex=nonpatt_type_regex)
    typeandsubtype_regex = '(?P<type>{type_regex})/(?P<subtype>{type_regex})'.format(type_regex=type_regex)
    params_regex = ';q=(?P<qvalue>(?:0(?:\.\d)?)|1(?:\.0)?)'
    mediarange_patt = re.compile('{0}(?:{1})?'.format(typeandsubtype_regex, params_regex))
    whitespacepatt = re.compile('\s+')

    content_type_patt = re.compile('^(?P<type>{nonpatt_type_regex})/(?P<subtype>{nonpatt_type_regex})$'.format(nonpatt_type_regex=nonpatt_type_regex))

    @classmethod
    def parse_content_type(cls, content_type):
        m = cls.content_type_patt.match(content_type)
        if m:
            return m.groups()
        else:
            raise ValueError('Invalid content-type: {0}'.format(content_type))

    def __init__(self):
        self.mediaranges = []

    def parse(self, header):
        header = self.whitespacepatt.sub('', header.lower()) # lowercase and strip whitespace to make it easier to parse.
        found = self.mediarange_patt.findall(header)
        for ttype, subtype, quality  in found:
            self._add(ttype, subtype, quality)
        self._sort()

    def _add(self, ttype, subtype, quality):
        self.mediaranges.append(MediaRange(ttype, subtype, quality))

    def _sort(self):
        self.mediaranges.sort()

    def __str__(self):
        return '; '.join(str(p) for p in self.mediaranges)

    def match(self, content_type):
        ttype, subtype = HttpAccessHeaderParser.parse_content_type(content_type)
        for mediarange in self.mediaranges:
            if mediarange.match(ttype, subtype):
                return True
        return False