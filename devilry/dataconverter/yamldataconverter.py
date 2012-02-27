from devilry.dataconverter.dataconverter import DataConverter
import yaml

class YamlDataConverter(DataConverter):
    """
    Convert data from and to YAML. Uses ``safe_load`` and ``safe_dump``, and
    the output is always *UTF-8* encoded.
    """
    @classmethod
    def fromPython(cls, obj, alternative_formats=[]):
        return yaml.safe_dump(obj, indent=4, default_flow_style=False, encoding='utf-8')

    @classmethod
    def toPython(cls, bytestring):
        return yaml.safe_load(bytestring)
