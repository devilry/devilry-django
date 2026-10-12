from django.test import TestCase
import htmls

from cradmin_legacy.renderable import AbstractRenderableWithCss
from cradmin_legacy.viewhelpers import listbuilder
from cradmin_legacy.python2_compatibility import mock


class MinimalRenderable(AbstractRenderableWithCss):
    template_name = "cradmin_viewhelpers_testapp/listbuilder/minimal-renderable.django.html"


class TestAbstractItemRenderer(TestCase):
    def test_without_valuealias(self):
        itemrenderer = listbuilder.base.AbstractItemRenderer(value="testvalue")
        self.assertEqual("testvalue", itemrenderer.value)

    def test_with_valuealias(self):
        class MyItemRenderer(listbuilder.base.AbstractItemRenderer):
            valuealias = "myvalue"

        itemrenderer = MyItemRenderer(value="testvalue")
        self.assertEqual("testvalue", itemrenderer.value)
        self.assertEqual("testvalue", itemrenderer.myvalue)


class TestItemValueRenderer(TestCase):
    def test_render(self):
        rendered = listbuilder.base.ItemValueRenderer(value="testvalue").render()
        selector = htmls.S(rendered)
        self.assertEqual("testvalue", selector.one(".cradmin-legacy-listbuilder-itemvalue").alltext_normalized)


class TestItemFrameRenderer(TestCase):
    def test_render(self):
        rendered = listbuilder.base.ItemFrameRenderer(
            inneritem=listbuilder.base.ItemValueRenderer(value="testvalue")
        ).render(request=mock.MagicMock())
        selector = htmls.S(rendered)
        self.assertTrue(selector.exists(".cradmin-legacy-listbuilder-itemframe"))
        self.assertEqual("testvalue", selector.one(".cradmin-legacy-listbuilder-itemvalue").alltext_normalized)


class TestList(TestCase):
    def test_append(self):
        testlist = listbuilder.base.List()
        renderable = MinimalRenderable()
        testlist.append(renderable)
        self.assertEqual([renderable], testlist.renderable_list)

    def test_extend(self):
        testlist = listbuilder.base.List()
        renderable1 = MinimalRenderable()
        renderable2 = MinimalRenderable()
        testlist.extend([renderable1, renderable2])
        self.assertEqual([renderable1, renderable2], testlist.renderable_list)

    def test_extend_with_values_without_frame_renderer_class(self):
        testlist = listbuilder.base.List()
        testlist.extend_with_values(
            ["testvalue1", "testvalue2"], value_renderer_class=listbuilder.base.ItemValueRenderer
        )
        self.assertEqual("testvalue1", testlist.renderable_list[0].value)
        self.assertEqual("testvalue2", testlist.renderable_list[1].value)
        self.assertTrue(isinstance(testlist.renderable_list[0], listbuilder.base.ItemValueRenderer))
        self.assertTrue(isinstance(testlist.renderable_list[1], listbuilder.base.ItemValueRenderer))

    def test_extend_with_values_with_frame_renderer_class(self):
        testlist = listbuilder.base.List()
        testlist.extend_with_values(
            ["testvalue1", "testvalue2"],
            value_renderer_class=listbuilder.base.ItemValueRenderer,
            frame_renderer_class=listbuilder.base.ItemFrameRenderer,
        )
        self.assertEqual("testvalue1", testlist.renderable_list[0].value)
        self.assertEqual("testvalue2", testlist.renderable_list[1].value)
        self.assertTrue(isinstance(testlist.renderable_list[0], listbuilder.base.ItemFrameRenderer))
        self.assertTrue(isinstance(testlist.renderable_list[1], listbuilder.base.ItemFrameRenderer))

    def test_extend_with_values_value_and_frame_renderer_kwargs_dict(self):
        testlist = listbuilder.base.List()
        testlist.extend_with_values(
            ["testvalue1", "testvalue2"],
            value_renderer_class=listbuilder.base.ItemValueRenderer,
            value_and_frame_renderer_kwargs={"extra_kwarg": 10},
        )
        self.assertEqual({"extra_kwarg": 10}, testlist.renderable_list[0].kwargs)
        self.assertEqual({"extra_kwarg": 10}, testlist.renderable_list[1].kwargs)

    def test_extend_with_values_value_and_frame_renderer_kwargs_function(self):
        def kwargs_function(value):
            if value == "testvalue1":
                return {"is_first": True}
            else:
                return {}

        testlist = listbuilder.base.List()
        testlist.extend_with_values(
            ["testvalue1", "testvalue2"],
            value_renderer_class=listbuilder.base.ItemValueRenderer,
            value_and_frame_renderer_kwargs=kwargs_function,
        )
        self.assertEqual({"is_first": True}, testlist.renderable_list[0].kwargs)
        self.assertEqual({}, testlist.renderable_list[1].kwargs)

    def test_from_value_iterable_without_frame_renderer_class(self):
        testlist = listbuilder.base.List.from_value_iterable(
            ["testvalue1", "testvalue2"], value_renderer_class=listbuilder.base.ItemValueRenderer
        )
        self.assertEqual("testvalue1", testlist.renderable_list[0].value)
        self.assertEqual("testvalue2", testlist.renderable_list[1].value)
        self.assertTrue(isinstance(testlist.renderable_list[0], listbuilder.base.ItemValueRenderer))
        self.assertTrue(isinstance(testlist.renderable_list[1], listbuilder.base.ItemValueRenderer))

    def test_from_value_iterable_with_frame_renderer_class(self):
        testlist = listbuilder.base.List.from_value_iterable(
            ["testvalue1", "testvalue2"],
            value_renderer_class=listbuilder.base.ItemValueRenderer,
            frame_renderer_class=listbuilder.base.ItemFrameRenderer,
        )
        self.assertEqual("testvalue1", testlist.renderable_list[0].value)
        self.assertEqual("testvalue2", testlist.renderable_list[1].value)
        self.assertTrue(isinstance(testlist.renderable_list[0], listbuilder.base.ItemFrameRenderer))
        self.assertTrue(isinstance(testlist.renderable_list[1], listbuilder.base.ItemFrameRenderer))

    def test_render(self):
        testlist = listbuilder.base.List()
        testlist.append(listbuilder.base.ItemValueRenderer(value="testvalue1"))
        testlist.append(listbuilder.base.ItemValueRenderer(value="testvalue2"))
        selector = htmls.S(testlist.render(request=mock.MagicMock()))
        self.assertEqual(2, selector.count("li"))
        self.assertEqual("testvalue1", selector.list("li")[0].alltext_normalized)
        self.assertEqual("testvalue2", selector.list("li")[1].alltext_normalized)
