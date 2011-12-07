class DataConverter(object):
    @classmethod
    def toPython(cls, obj):
        raise NotImplementedError()

    @classmethod
    def fromPython(cls, bytestring):
        raise NotImplementedError()