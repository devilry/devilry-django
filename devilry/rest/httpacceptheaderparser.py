import re
from devilry.rest.error import InvalidContentTypeError


class HttpAcceptHeaderParseError(InvalidContentTypeError):
    """
    Raised for errors in :class:`HttpAccessHeaderParse`.
    """

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

    def match(self, *content_types):
        for ttype, subtype in content_types:
            if self._match(ttype, subtype):
                return ttype + '/' + subtype
        return False

    def _match(self, ttype, subtype):
        return self._typematch(self.ttype, ttype) and self._typematch(self.subtype, subtype)

    def _typematch(self, patt, ttype):
        return patt == '*' or patt == ttype

    def __str__(self):
        return '{ttype}/{subtype};q={quality}'.format(**self.__dict__)

class HttpAcceptHeaderParser(object):
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
            raise HttpAcceptHeaderParseError('Invalid content-type: {0}'.format(content_type))

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

    def match(self, *content_types):
        content_types = [HttpAcceptHeaderParser.parse_content_type(content_type) for content_type in content_types]
        for mediarange in self.mediaranges:
            match = mediarange.match(*content_types)
            if match:
                return match
        raise HttpAcceptHeaderParseError('No matching content-types for: {0}'.format(self))