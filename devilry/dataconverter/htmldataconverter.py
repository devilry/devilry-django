from urlparse import urlparse
from xml.etree import ElementTree
from devilry.dataconverter.dataconverter import DataConverter
from devilry.dataconverter.utils import str_format_datetime

style = """
    body {
        font-family: sans-serif;
        margin: 0;
        padding: 0 30px;
    }
    body>dl>dt {
        border-top: 3px solid #eee;
        color: #888;
        margin-top: 30px;
        font-size: 1.8em;
        font-weight: bold;
    }
    body>dl>dd {
        margin-left: 0;
    }
    body>dl>dd dt {
        font-weight: bold;
    }
"""

class ToHtml(object):
    def __init__(self, obj):
        self.obj = obj

    def encode(self):
        body = ElementTree.Element("body")
        self._encode(body, self.obj)
        return ElementTree.tostring(body, encoding='utf-8')

    def _encode(self, parent, data):
        typename = type(data).__name__
        name = "encode_" + typename
        if hasattr(self, name):
            getattr(self, name)(parent, data)
        else:
            raise ValueError("Unsupported data type: {0}".format(typename))

    def encode_dict(self, parent, data):
        dl = ElementTree.SubElement(parent, "dl")
        for key, value in data.iteritems():
            keyelem = ElementTree.SubElement(dl, 'dt')
            keyelem.text = key
            valueelem = ElementTree.SubElement(dl, 'dd')
            self._encode(valueelem, value)

    def encode_list(self, parent, data):
        ul = ElementTree.SubElement(parent, "ul")
        for value in data:
            item = ElementTree.SubElement(ul, "li")
            self._encode(item, value)


    def encode_unicode(self, parent, data):
        url = urlparse(data)
        if url.scheme or data.startswith('/'):
            a = ElementTree.SubElement(parent, "a", href=data)
            a.text = data
        else:
            parent.text = data

    def encode_str(self, parent, data):
        self.encode_unicode(parent, data)

    def encode_datetime(self, parent, data):
        parent.text = str_format_datetime(data)

    def encode_int(self, parent, data):
        parent.text = str(data)

    def encode_NoneType(self, parent, data):
        parent.text = 'None'


class HtmlDataConverter(DataConverter):
    @classmethod
    def fromPython(cls, obj):
        return '<html><head><style type="text/css">{0}</style></head>{1}</html>'.format(style, ToHtml(obj).encode())

    @classmethod
    def toPython(cls, bytestring):
        raise NotImplementedError("The HTML data converter can not be used for input.")
