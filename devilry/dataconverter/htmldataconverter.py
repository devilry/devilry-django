from urllib import urlencode
from urlparse import urlparse
from xml.etree import ElementTree
from django.template.loader import render_to_string
from devilry.dataconverter.dataconverter import DataConverter
from devilry.dataconverter.utils import str_format_datetime


class ToHtml(object):
    def __init__(self, obj, alternative_formats=[]):
        self.alternative_formats = alternative_formats
        self.obj = obj

    def encode(self):
        body = ElementTree.Element("body")
        if self.alternative_formats:
            self.add_alternative_formats(body)
        dataheading = ElementTree.SubElement(body, 'h1')
        dataheading.text = 'Data'
        self._encode(body, self.obj)
        return ElementTree.tostring(body, encoding='utf-8')

    def add_alternative_formats(self, body):
        heading = ElementTree.SubElement(body, 'h1')
        heading.text = 'Alternative formats'
        ul = ElementTree.SubElement(body, "ul")
        for content_type in self.alternative_formats:
            li = ElementTree.SubElement(ul, "li")
            onclick = 'open_alternative_format("{0}")'.format(content_type)
            a = ElementTree.SubElement(li, "a", href="#",
                                       onclick=onclick)
            a.text = content_type

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

    def encode_bool(self, parent, data):
        parent.text = str(data)


class HtmlDataConverter(DataConverter):
    @classmethod
    def fromPython(cls, obj, alternative_formats=[]):
        return render_to_string('dataconverter/htmldataconverter.django.html', {
            "body": ToHtml(obj, alternative_formats).encode()
        })

    @classmethod
    def toPython(cls, bytestring):
        raise NotImplementedError("The HTML data converter can not be used for input.")
