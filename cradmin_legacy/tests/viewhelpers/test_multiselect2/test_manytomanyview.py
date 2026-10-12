import htmls
from unittest import mock
from django import test
from django.http import QueryDict

from cradmin_legacy.viewhelpers import listbuilder
from cradmin_legacy.viewhelpers.multiselect2 import manytomanyview


class TestViewMixin(test.TestCase):
    def test_get_selected_values_list(self):
        view = manytomanyview.ViewMixin()
        view.request = mock.MagicMock()
        view.request.GET = QueryDict("", mutable=True)
        view.request.GET.update({"manytomany_select_current_value": "[1,2]"})
        self.assertEqual([1, 2], view.get_selected_values_list())

    def test_get_selected_objects(self):
        view = manytomanyview.ViewMixin()
        view.request = mock.MagicMock()
        view.request.cradmin_role = "testrole"
        view.get_selected_values_list = mock.MagicMock(return_value="testvalue")
        mockqueryset = mock.MagicMock()
        view.get_queryset_for_role = mock.MagicMock(return_value=mockqueryset)

        view.get_selected_objects()
        mockqueryset.filter.assert_called_once_with(pk__in="testvalue")
        view.get_queryset_for_role.assert_called_once_with("testrole")

    def test_get_selected_objects_has_get_unfiltered_queryset_for_role_method(self):
        view = manytomanyview.ViewMixin()
        view.request = mock.MagicMock()
        view.request.cradmin_role = "testrole"
        view.get_selected_values_list = mock.MagicMock(return_value="testvalue")
        view.get_queryset_for_role = mock.MagicMock()
        mockqueryset = mock.MagicMock()
        view.get_unfiltered_queryset_for_role = mock.MagicMock(return_value=mockqueryset)

        view.get_selected_objects()
        mockqueryset.filter.assert_called_once_with(pk__in="testvalue")
        view.get_unfiltered_queryset_for_role.assert_called_once_with("testrole")
        view.get_queryset_for_role.assert_not_called()

    def test_should_include_previously_selected_no_paging_no_get_filters_string(self):
        view = manytomanyview.ViewMixin()
        self.assertTrue(view.should_include_previously_selected())

    def test_should_include_previously_selected_get_filters_string_empty_string(self):
        view = manytomanyview.ViewMixin()
        view.get_filters_string = mock.MagicMock(return_value="")
        self.assertTrue(view.should_include_previously_selected())

    def test_should_include_previously_selected_get_filters_string_nonempty_string(self):
        view = manytomanyview.ViewMixin()
        view.get_filters_string = mock.MagicMock(return_value="test")
        self.assertFalse(view.should_include_previously_selected())

    def test_should_include_previously_selected_paginate_by_no_page_specified(self):
        view = manytomanyview.ViewMixin()
        view.paginate_by = 40
        view.page_kwarg = "page"
        view.kwargs = {}
        view.request = mock.MagicMock()
        view.request.GET = {}
        self.assertTrue(view.should_include_previously_selected())

    def test_should_include_previously_selected_paginate_by_page1_kwargs(self):
        view = manytomanyview.ViewMixin()
        view.paginate_by = 40
        view.page_kwarg = "page"
        view.kwargs = {"page": 1}
        view.request = mock.MagicMock()
        view.request.GET = {}
        self.assertTrue(view.should_include_previously_selected())

    def test_should_include_previously_selected_paginate_by_page1_requestget(self):
        view = manytomanyview.ViewMixin()
        view.paginate_by = 40
        view.page_kwarg = "page"
        view.kwargs = {}
        view.request = mock.MagicMock()
        view.request.GET = {"page": 1}
        self.assertTrue(view.should_include_previously_selected())

    def test_should_include_previously_selected_paginate_by_page2_kwargs(self):
        view = manytomanyview.ViewMixin()
        view.paginate_by = 40
        view.page_kwarg = "page"
        view.kwargs = {"page": 2}
        view.request = mock.MagicMock()
        view.request.GET = {}
        self.assertFalse(view.should_include_previously_selected())

    def test_should_include_previously_selected_paginate_by_page2_requestget(self):
        view = manytomanyview.ViewMixin()
        view.paginate_by = 40
        view.page_kwarg = "page"
        view.kwargs = {}
        view.request = mock.MagicMock()
        view.request.GET = {"page": 2}
        self.assertFalse(view.should_include_previously_selected())

    def test_get_queryset_for_role_should_include_previously_selected_false(self):
        mockqueryset = mock.MagicMock()

        class SuperMyView:
            def get_queryset_for_role(self, role):
                return mockqueryset

        class MyView(manytomanyview.ViewMixin, SuperMyView):
            pass

        view = MyView()
        view.request = mock.MagicMock()
        view.should_include_previously_selected = mock.MagicMock(return_value=False)
        view.get_queryset_for_role()
        mockqueryset.exclude.assert_not_called()

    def test_get_queryset_for_role_should_include_previously_selected_true(self):
        mockqueryset = mock.MagicMock()

        class SuperMyView:
            def get_queryset_for_role(self, role):
                return mockqueryset

        class MyView(manytomanyview.ViewMixin, SuperMyView):
            pass

        view = MyView()
        view.request = mock.MagicMock()
        view.should_include_previously_selected = mock.MagicMock(return_value=True)
        view.get_selected_values_list = mock.MagicMock(return_value="testvalue")
        view.get_queryset_for_role()
        mockqueryset.exclude.assert_called_once_with(pk__in="testvalue")

    def test_get_target_renderer_class(self):
        view = manytomanyview.ViewMixin()
        self.assertEqual(manytomanyview.ViewMixin.target_renderer_class, view.get_target_renderer_class())

    def test_get_target_renderer_kwargs(self):
        view = manytomanyview.ViewMixin()
        view.request = mock.MagicMock()
        view.request.GET = {"manytomany_select_fieldid": "testid", "manytomany_select_required": "True"}
        target_renderer_kwargs = view.get_target_renderer_kwargs()
        self.assertEqual("testid", target_renderer_kwargs["target_formfield_id"])
        self.assertFalse(target_renderer_kwargs["empty_selection_allowed"])

    def test_get_target_renderer(self):
        view = manytomanyview.ViewMixin()
        view.request = mock.MagicMock()
        view.request.GET = {"manytomany_select_fieldid": "testid", "manytomany_select_required": "True"}
        target_renderer = view.get_target_renderer()
        self.assertEqual("testid", target_renderer.target_formfield_id)


class TestListBuilderViewMixin(test.TestCase):
    def test_get_listbuilder_list_should_include_previously_selected_false(self):
        class SuperMyView:
            def get_listbuilder_list(self, context):
                return listbuilder.base.List()

        class MyView(manytomanyview.ListBuilderViewMixin, SuperMyView):
            pass

        view = MyView()
        view.should_include_previously_selected = mock.MagicMock(return_value=False)
        self.assertFalse(view.get_listbuilder_list(context={}).has_items())

    def test_get_listbuilder_list_should_include_previously_selected_true(self):
        class SuperMyView:
            def get_listbuilder_list(self, context):
                return listbuilder.base.List()

        class MyView(manytomanyview.ListBuilderViewMixin, SuperMyView):
            pass

        view = MyView()
        view.should_include_previously_selected = mock.MagicMock(return_value=True)
        view.get_value_renderer_class = mock.MagicMock(return_value=listbuilder.base.ItemValueRenderer)
        view.get_frame_renderer_class = mock.MagicMock(return_value=listbuilder.base.ItemFrameRenderer)
        view.get_selected_objects = mock.MagicMock(return_value=["testvalue"])
        selector = htmls.S(view.get_listbuilder_list(context={}).render())
        self.assertTrue("testvalue", selector.one(".cradmin-legacy-listbuilder-itemvalue").alltext_normalized)


class ListBuilderFilterListViewMixin(test.TestCase):
    def test_get_filterlist_url(self):
        view = manytomanyview.ListBuilderFilterListViewMixin()
        view.request = mock.MagicMock()
        view.get_filterlist_url(filters_string="test")
        view.request.cradmin_app.reverse_appurl.assert_called_once_with(
            "manytomanyselect-filter", kwargs={"filters_string": "test"}
        )

    def test_add_target_renderer_to_filterlist(self):
        view = manytomanyview.ListBuilderFilterListViewMixin()
        view.get_target_renderer = mock.MagicMock(return_value="testrenderer")
        mockfilterlist = mock.MagicMock()
        view.add_target_renderer_to_filterlist(filterlist=mockfilterlist)
        mockfilterlist.append.assert_called_once_with("testrenderer")

    def test_add_filterlist_items(self):
        class SuperMyView:
            def add_filterlist_items(self, filterlist):
                pass

        class MyView(manytomanyview.ListBuilderFilterListViewMixin, SuperMyView):
            pass

        view = MyView()
        view.add_target_renderer_to_filterlist = mock.MagicMock()
        view.add_filterlist_items("testfilterlist")
        view.add_target_renderer_to_filterlist.assert_called_once_with(filterlist="testfilterlist")
