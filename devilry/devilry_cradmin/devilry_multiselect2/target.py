class SelectedCountTargetMixin:
    """
    Mixin for :class:`cradmin_legacy.viewhelpers.multiselect2.target_renderer.Target`
    subclasses that adds the number of selected items to the title,
    resulting in ``"<with items title> (<count>)"``.

    The count is updated dynamically by the ``devilry-multiselect2-selected-count``
    webcomponent when items are selected or deselected.
    """

    template_name = "devilry_cradmin/devilry_multiselect2/target-with-selected-count.django.html"
