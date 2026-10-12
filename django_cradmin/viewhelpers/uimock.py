from django.shortcuts import redirect

from . import generic


class UiMock(generic.StandaloneBaseTemplateView):
    """
    View for UI mocks.

    See :doc:`viewhelpers_uimock` for details.
    """

    #: Template directory (prefix for the templates of all the mocks).
    #:
    #: Must end with ``/``. The directory must contain an ``index.django.html`` template.
    #:
    #: You typically send this as an argument to ``UiMock.as_view()`` (I.E.: you
    #: normally do not need to subclass UiMock).
    #:
    #: See :meth:`.get_template_names` for details on how this is used.
    template_directory = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.template_directory:
            raise ValueError("The UiMock class requires a template_directory as argument to as_view().")
        if not self.template_directory.endswith("/"):
            raise ValueError("The template_directory kwarg for UiMock must end with /")

    def dispatch(self, request, mockname=None, **kwargs):
        """

        Args:
            request: The HttpRequest.
            mockname: The name of the requested mock. We expect that a template named
                ``<mockname>.django.html`` is available in :obj:`~.UiMock.template_directory`.
            **kwargs: Other view kwargs (future proofing).

        Returns:

        """
        self.session_postdata = None
        self.mockname = mockname
        if "cradmin_uimock_postdata" in self.request.session:
            self.session_postdata = self.request.session["cradmin_uimock_postdata"]
            if "csrfmiddlewaretoken" in self.session_postdata:
                del self.session_postdata["csrfmiddlewaretoken"]
            del self.request.session["cradmin_uimock_postdata"]

        return super().dispatch(request, mockname, **kwargs)

    def _get_mock_template_name(self, mockname=None):
        template_name = "index.django.html"
        if mockname:
            template_name = "{}.django.html".format(mockname)
        template_name = "{}{}".format(self.template_directory, template_name)
        return template_name

    def get_template_names(self):
        """
        Looks up a template in the :obj:`~.UiMock.template_directory` by the following rules:

        - If we DO NOT have a ``mockname`` in view kwargs (see :meth:`.dispatch`), we
          return ``<template_directory>/index.django.html``.
        - If we have a ``mockname`` in view kwargs (see :meth:`.dispatch`), we
          return ``<template_directory>/<mockname>.django.html``.
        """
        return [
            self._get_mock_template_name(mockname=self.mockname),
            self._get_mock_template_name(mockname="404"),
            "django_cradmin/viewhelpers/uimock/404.django.html",
        ]

    def post(self, request, *args, **kwargs):
        """
        Sets ``request.POST`` data as a session variable, ``cradmin_uimock_postdata``,
        and redirects to the current full URL. In dispatch(), we pop this from session
        and adds it as the ``postdata`` template context data.

        This facilitates mocking simple form flows.
        """
        self.request.session["cradmin_uimock_postdata"] = self.request.POST.dict()
        return redirect(self.request.get_full_path())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["postdata"] = self.session_postdata
        context["mockname"] = self.mockname
        return context
