from devilry.dataconverter.dataconverter import DataConverter
import yaml

class YamlDataConverter(DataConverter):
    @classmethod
    def fromPython(cls, obj):
        return yaml.safe_dump(obj, indent=4, default_flow_style=False, encoding='utf-8')

    @classmethod
    def toPython(cls, bytestring):
        return yaml.safe_load(bytestring)