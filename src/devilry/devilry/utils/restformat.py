import warnings
warnings.warn("devilry.utils.restformat is deprecated. Use devilry_rest.serializehelpers instead.", DeprecationWarning)
from devilry_rest.serializehelpers import format_datetime
from devilry_rest.serializehelpers import format_timedelta
from devilry_rest.serializehelpers import serialize_user
