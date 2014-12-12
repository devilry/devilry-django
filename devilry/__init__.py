from pkg_resources import resource_string
import json

__version__ = json.loads(resource_string(__name__, 'version.json'))
