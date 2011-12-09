from xml.etree import cElementTree as ElementTree
from devilry.dataconverter.dataconverter import DataConverter
from devilry.dataconverter.utils import str_format_datetime


class ToXml(object):
    def __init__(self, obj):
        self.obj = obj

    def encode(self, rootelement="data"):
        root = ElementTree.Element(rootelement)
        self._encode(root, self.obj)
        return ElementTree.tostring(root, encoding='utf-8')

    def _encode(self, parent, data):
        typename = type(data).__name__
        name = "encode_" + typename
        if hasattr(self, name):
            getattr(self, name)(parent, data)
        else:
            raise ValueError("Unsupported data type: {0}".format(typename))

    def encode_dict(self, parent, data):
        for key, value in data.iteritems():
            item = ElementTree.SubElement(parent, key)
            self._encode(item, value)

    def encode_list(self, parent, data):
        for value in data:
            item = ElementTree.SubElement(parent, "item")
            self._encode(item, value)


    def encode_unicode(self, parent, data):
        parent.text = data

    def encode_str(self, parent, data):
        parent.text = data

    def encode_datetime(self, parent, data):
        parent.text = str_format_datetime(data)

    def encode_int(self, parent, data):
        parent.text = str(data)

    def encode_NoneType(self, parent, data):
        parent.text = ''


class XmlDataConverter(DataConverter):
    @classmethod
    def fromPython(cls, obj, alternative_formats=[]):
        return ToXml(obj).encode()

    @classmethod
    def toPython(cls, bytestring):
        pass
