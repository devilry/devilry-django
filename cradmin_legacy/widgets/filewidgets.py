import posixpath

from django import forms
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe


class ImageWidget(forms.ClearableFileInput):
    """
    Clearable image widget.

    Can be made un-clearable (for required fields) using the
    ``clearable`` argument for ``__init__``.
    """

    template_name = "cradmin_legacy/filewidgets/imagewidget.django.html"

    #: Comma separated string of filetypes that we should accept.
    #: Added to the file upload field as the accept attribute.
    #: Defaults to ``"image/png,image/jpeg,image/gif"``.
    accept = "image/*"

    def __init__(self, request, attrs=None, template_name=None, clearable=True, preview_imagetype=None):
        self.request = request
        self.clearable = clearable
        if template_name:
            self.template_name = template_name
        self.preview_imagetype = preview_imagetype
        self.preview_fallback_options = {"width": 300, "height": 300}

        super().__init__(attrs)

    def get_preview_css_styles(self):
        if self.preview_imagetype:
            options = settings.CRADMIN_LEGACY_IMAGEUTILS_IMAGETYPE_MAP[self.preview_imagetype]
        else:
            options = self.preview_fallback_options
        styles = []
        if "width" in options:
            styles.append("max-width: {}px".format(options["width"]))
        else:
            styles.append("max-width: 100%".format(options["width"]))
        return styles

    def build_preview_url(self, imagepath):
        if imagepath:
            return posixpath.join(settings.MEDIA_URL, imagepath)
        else:
            return None

    def get_context_data(self, imageurl, name, value, attrs):
        return {
            "imageurl": imageurl,
            "clear_checkbox_name": self.clear_checkbox_name(name),
            "clearable": self.clearable,
            "preview_imagetype": self.preview_imagetype,
            "preview_fallback_options": self.preview_fallback_options,
            "preview_css_styles": ";".join(self.get_preview_css_styles()),
            "widget": {"type": "file", "name": name, "value": value, "attrs": attrs},
        }

    def render(self, name, value, attrs=None, renderer=None):
        attrs = attrs or {}
        attrs["cradmin-legacy-image-preview-filefield"] = ""
        if self.accept:
            attrs["accept"] = self.accept
        attrs["cradmin-filefield-value"] = value or ""
        imagepath = getattr(value, "name", None)
        imageurl = self.build_preview_url(imagepath)
        context_data = self.get_context_data(imageurl=imageurl, name=name, value=value, attrs=attrs)
        output = render_to_string(self.template_name, context_data, request=self.request)
        return mark_safe(output)


class FileWidget(forms.ClearableFileInput):
    """
    Clearable file widget.

    Can be made un-clearable (for required fields) using the
    ``clearable`` argument for ``__init__``.
    """

    template_name = "cradmin_legacy/filewidgets/filewidget.django.html"

    #: Comma separated string of filetypes that we should accept.
    #: Added to the file upload field as the accept attribute.
    #: Defaults to ``None``, which means that all filetypes are allowed.
    #: Example: ``"application/pdf,application/msword,text/plain"``.
    accept = None

    def __init__(self, attrs=None, template_name=None, clearable=True):
        self.clearable = clearable
        if template_name:
            self.template_name = template_name
        super().__init__(attrs)

    def render(self, name, value, attrs=None, renderer=None):
        attrs = attrs or {}
        if self.accept:
            attrs["accept"] = self.accept
        attrs["cradmin-filefield-value"] = value or ""
        # input_html = forms.FileInput.render(self, name, value, attrs)
        file_path = getattr(value, "name", None)
        if file_path:
            file_name = posixpath.basename(file_path)
        else:
            file_name = None

        output = render_to_string(
            self.template_name,
            {
                # 'input_html': input_html,
                "file_path": file_path,
                "file_name": file_name,
                "MEDIA_URL": settings.MEDIA_URL,
                "clear_checkbox_name": self.clear_checkbox_name(name),
                "clearable": self.clearable,
                "widget": {"type": "file", "name": name, "value": value, "attrs": attrs},
            },
        )
        return mark_safe(output)
