from django.conf import settings
from django.utils.module_loading import import_string


_backend = None


def get_backend():
    """
    Get the configured imageutils backend, defaulting to and object of
    class:`cradmin_legacy.imageutils.backends.sorl_thumbnail.SorlThumbnail`
    if the :setting:`CRADMIN_LEGACY_IMAGEUTILS_BACKEND` setting is not defined.
    """
    global _backend
    if not _backend:
        backendclasspath = getattr(
            settings,
            "CRADMIN_LEGACY_IMAGEUTILS_BACKEND",
            "cradmin_legacy.imageutils.backends.sorl_thumbnail.SorlThumbnail",
        )
        _backend = import_string(backendclasspath)()
    return _backend
