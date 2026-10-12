from django.test import TestCase

from cradmin_legacy.renderable import AbstractRenderable


class MinimalRenderable(AbstractRenderable):
    template_name = "cradmin_viewhelpers_testapp/listbuilder/minimal-renderable.django.html"


class TestAbstractRenderable(TestCase):
    def test_get_template_name_no_template_name(self):
        with self.assertRaises(NotImplementedError):
            AbstractRenderable().get_template_name()

    def test_get_template_name_has_template_name(self):
        MinimalRenderable().get_template_name()  # NotImplementedError not raised

    def test_get_context_data(self):
        renderable = AbstractRenderable()
        self.assertEqual({"me": renderable}, renderable.get_context_data())

    def test_render(self):
        self.assertEqual("Test", MinimalRenderable().render().strip())
