from django.conf import settings


class ImageTypeMapSettingNotDefined(Exception):
    """
    Raised when :meth:`.Interface.transform_image_using_imagetype` is called
    when the ``CRADMIN_LEGACY_IMAGEUTILS_IMAGETYPE_MAP`` setting is not defined.
    """


class InvalidImageType(Exception):
    """
    Raised when :meth:`.Interface.transform_image_using_imagetype` is called
    with an ``imagetype`` not in the ``CRADMIN_LEGACY_IMAGEUTILS_IMAGETYPE_MAP``
    setting.
    """


class Interface:
    """
    Imageutils backend interface.

    An object of subclass of this interface is loaded via the
    ``CRADMIN_LEGACY_IMAGEUTILS_BACKEND`` setting, and the object
    is a singleton that only has one instance for the entire
    Django server process.
    """

    def transform_image(self, imageurl, **options):
        """
        Transforms the given ``imageurl`` by applying the
        given options and returns the URL of the transformed image.

        All backends must support the following options:

        - ``width``: The width to scale the image to.
        - ``height``: The height to scale the image to.
        - ``quality``: The quality to transform the image to
          as an int between 0 and 100 (100 means 100% quality).
          Should default to 100.
        - ``crop``: Specifies how to crop the image. All backends must
          support the following values:

          - ``limit`` (default): The image should be scaled to not exceed the specified
            width and/or height while retaining original aspect ratio of the image.
          - ``fill``: The image should be cropped to fill the specified ``width`` and ``height``
            while retaining original proportions of the image.

        This method must be overridden for each backend.
        """
        raise NotImplementedError()

    def transform_image_using_imagetype(self, imageurl, imagetype):
        """
        Works just like :meth:`.transform_image`, except that the
        options is retrieved from the :setting:`CRADMIN_LEGACY_IMAGEUTILS_IMAGETYPE_MAP` setting.

        Raises :exc:`.ImageTypeMapSettingNotDefined` if the :setting:`CRADMIN_LEGACY_IMAGEUTILS_IMAGETYPE_MAP`
        setting is not defined.

        Raises :exc:`.InvalidImageType` if the ``imagetype`` key is not defined in
        the :setting:`CRADMIN_LEGACY_IMAGEUTILS_IMAGETYPE_MAP` setting.
        """
        if not hasattr(settings, "CRADMIN_LEGACY_IMAGEUTILS_IMAGETYPE_MAP"):
            raise ImageTypeMapSettingNotDefined("The CRADMIN_LEGACY_IMAGEUTILS_IMAGETYPE_MAP setting is not defined.")
        try:
            options = settings.CRADMIN_LEGACY_IMAGEUTILS_IMAGETYPE_MAP[imagetype]
        except KeyError:
            raise InvalidImageType(
                "The requested imagetype, {}, is not specified in the "
                "CRADMIN_LEGACY_IMAGEUTILS_IMAGETYPE_MAP setting.".format(imagetype)
            )
        return self.transform_image(imageurl, **options)
