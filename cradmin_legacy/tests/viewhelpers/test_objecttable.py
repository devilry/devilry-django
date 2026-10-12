import htmls
from cradmin_legacy.python2_compatibility import mock
from django.test import TestCase, RequestFactory

from cradmin_legacy.tests.viewhelpers.cradmin_viewhelpers_testapp.models import TestModel
from cradmin_legacy.viewhelpers import objecttable
from cradmin_legacy.cradmin_legacy_testapp import models as testmodels


class TestColumn(TestCase):
    def setUp(self):
        class TestColSubclass(objecttable.Column):
            modelfield = "testfield"

            def __init__(self, **kwargs):
                super().__init__(**kwargs)

        self.model_testobject = TestModel()
        view = mock.MagicMock()
        view.model = self.model_testobject
        self.column_subclass = TestColSubclass(view=view, columnindex=0)

    def test_get_header_not_implemented(self):
        test = objecttable.Column(view=None, columnindex=0)

        with self.assertRaises(NotImplementedError):
            test.get_header()

    def test_get_header(self):
        self.assertEqual("Test Value", self.column_subclass.get_header())

    def test_render_value(self):
        self.model_testobject.testfield = "test_value"
        self.assertEqual("test_value", self.column_subclass.render_value(self.model_testobject))

    # check that you get an exception when running render_value without having modelfield..
    def test_render_value_not_implemented(self):
        col = objecttable.Column(view=None, columnindex=0)

        with self.assertRaises(NotImplementedError):
            col.render_value(None)

    # check that you get an exception when running render_cell_content without overriding with subclass..
    def test_render_cell_not_implemented(self):
        col = objecttable.Column(view=mock.MagicMock(), columnindex=0)

        with self.assertRaises(NotImplementedError):
            col.render_cell_content(None)


class TestPlainTextColumn(TestCase):
    def setUp(self):
        class TestColSubclass(objecttable.PlainTextColumn):
            modelfield = "testfield"

            def __init__(self, **kwargs):
                super().__init__(**kwargs)

        self.model_testobject = TestModel()
        view = mock.MagicMock()
        view.model = self.model_testobject
        self.column_subclass = TestColSubclass(view=view, columnindex=0)

    def test_render_cell(self):
        self.model_testobject.testfield = "test_value"
        self.assertEqual(
            '<span class="objecttable-cellvalue">test_value</span>',
            self.column_subclass.render_cell_content(self.model_testobject).strip(),
        )


class TestSingleActionColumn(TestCase):
    def setUp(self):
        class TestIncompleteColSubclass(objecttable.SingleActionColumn):
            modelfield = "testfield"

            def __init__(self, **kwargs):
                super().__init__(**kwargs)

        class TestColSubclass(objecttable.SingleActionColumn):
            modelfield = "testfield"

            def __init__(self, **kwargs):
                super().__init__(**kwargs)

            def get_actionurl(self, obj):
                return f"www.example.com/{obj.testfield}"

        self.model_testobject = TestModel(testfield="test_value")
        view = mock.MagicMock()
        view.model = self.model_testobject
        self.column_subclass = TestColSubclass(view=view, columnindex=0)
        self.column_subclass_incomplete = TestIncompleteColSubclass(view=view, columnindex=0)

    def test_get_actionurl_ExceptionRaised(self):
        with self.assertRaises(NotImplementedError):
            self.column_subclass_incomplete.get_actionurl(self.model_testobject)

    def test_render_cell_ExceptionRaised(self):
        with self.assertRaises(NotImplementedError):
            self.column_subclass_incomplete.render_cell_content(self.model_testobject)

    def test_render_cell(self):
        expected = '<a href="www.example.com/test_value" class="objecttable-cellvalue-link">test_value</a>'
        self.assertEqual(self.column_subclass.render_cell_content(self.model_testobject), expected)


class TestMultiActionColumn(TestCase):
    def setUp(self):
        class TestIncompleteColSubclass(objecttable.MultiActionColumn):
            modelfield = "testfield"

            def __init__(self, **kwargs):
                super().__init__(**kwargs)

        class TestColSubclass(objecttable.MultiActionColumn):
            modelfield = "testfield"

            def __init__(self, **kwargs):
                super().__init__(**kwargs)

            def get_buttons(self, obj):
                return [
                    objecttable.Button(label="Btn1", url="www.example.com/btn1"),
                    objecttable.Button(label="Btn2", url="www.example.com/btn2"),
                ]

        self.model_testobject = TestModel(testfield="test_value")
        view = mock.MagicMock()
        view.model = self.model_testobject
        self.column_subclass = TestColSubclass(view=view, columnindex=0)
        self.column_subclass_incomplete = TestIncompleteColSubclass(view=view, columnindex=0)

    def test_get_buttons_ExceptionRaised(self):
        with self.assertRaises(NotImplementedError):
            self.column_subclass_incomplete.get_buttons(self.model_testobject)

    def test_render_cell_ExceptionRaised(self):
        with self.assertRaises(NotImplementedError):
            self.column_subclass_incomplete.render_cell_content(self.model_testobject)

    def test_render_cell(self):
        result = self.column_subclass.render_cell_content(self.model_testobject)
        selector = htmls.S(result)
        self.assertEqual(selector.one("p.objecttable-cellvalue").alltext_normalized, "test_value")
        self.assertTrue(selector.exists("p.objecttable-cellbuttons"))
        self.assertEqual(selector.count("a"), 2)


class TestButton(TestCase):
    def test_render_with_icon_and_class(self):
        btn = objecttable.Button(
            label="My Btn",
            url="www.example.com/mybtnurl",
            buttonclass="btn btn-danger btn-sm",
            icon="glyphicon glyphicon-shopping-cart",
        )
        selector = htmls.S(btn.render())
        self.assertEqual(selector.one("a")["href"], "www.example.com/mybtnurl")
        self.assertEqual(selector.one("a")["class"], "btn btn-danger btn-sm")
        self.assertEqual(selector.one("a").alltext_normalized, "My Btn")
        self.assertEqual(selector.one("a span")["class"], "glyphicon glyphicon-shopping-cart")

    def test_render_simple(self):
        btn = objecttable.Button(label="My Btn", url="www.example.com/mybtnurl")
        selector = htmls.S(btn.render())
        self.assertEqual(selector.one("a")["href"], "www.example.com/mybtnurl")
        self.assertEqual(selector.one("a")["class"], "btn btn-default btn-sm")
        self.assertEqual(selector.one("a").alltext_normalized, "My Btn")


class TestOrderingStringParser(TestCase):
    def test_parse_empty(self):
        orderingqueryarg = objecttable.OrderingStringParser("")
        self.assertEqual(len(orderingqueryarg.orderingdict), 0)

    def test_parse_single(self):
        orderingqueryarg = objecttable.OrderingStringParser("a3")
        self.assertEqual(len(orderingqueryarg.orderingdict), 1)
        self.assertTrue(orderingqueryarg.orderingdict[3])

    def test_parse_multi(self):
        orderingqueryarg = objecttable.OrderingStringParser("a3.d1")
        self.assertEqual(len(orderingqueryarg.orderingdict), 2)
        self.assertTrue(orderingqueryarg.orderingdict[3].order_ascending)
        self.assertFalse(orderingqueryarg.orderingdict[1].order_ascending)

    def test_remove_column(self):
        self.assertEqual(objecttable.OrderingStringParser("a3.d1.a6").remove_column(6), "a3.d1")
        self.assertEqual(objecttable.OrderingStringParser("a3.d1.a6").remove_column(1), "a3.a6")

    def test_remove_nonexisting_colum(self):
        self.assertEqual(objecttable.OrderingStringParser("").remove_column(2), "")
        self.assertEqual(objecttable.OrderingStringParser("a1").remove_column(2), "a1")
        self.assertEqual(objecttable.OrderingStringParser("a3.d1.a6").remove_column(2), "a3.d1.a6")

    def test_flip_existing_column(self):
        self.assertEqual(objecttable.OrderingStringParser("d1").flip_column(1), "a1")
        self.assertEqual(objecttable.OrderingStringParser("a3.d1.a6").flip_column(1), "a3.a1.a6")
        self.assertEqual(objecttable.OrderingStringParser("a3.d1.a6").flip_column(3), "d3.d1.a6")

    def test_flip_new_column(self):
        self.assertEqual(objecttable.OrderingStringParser("").flip_column(1), "a1")
        self.assertEqual(objecttable.OrderingStringParser("a3").flip_column(1), "a3.a1")


class TestObjectTableView(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _mock_request(self, request):
        request.cradmin_role = mock.MagicMock()
        request.cradmin_app = mock.MagicMock()

    def test_empty(self):
        class MyObjectTableView(objecttable.ObjectTableView):
            model = testmodels.SomeItem

            def get_queryset_for_role(self, role):
                return testmodels.SomeItem.objects.none()

        request = self.factory.get("/test")
        self._mock_request(request)
        response = MyObjectTableView.as_view()(request)
        response.render()
        selector = htmls.S(response.content)
        # selector.one('#cradmin_legacy_contentwrapper').prettyprint()
        self.assertFalse(selector.exists("#objecttableview-table"))
        self.assertEqual(selector.one("#objecttableview-no-items-message").alltext_normalized, "No some items")

    def test_empty_hide_search(self):
        class MyObjectTableView(objecttable.ObjectTableView):
            model = testmodels.SomeItem
            searchfields = ["name"]

            def get_queryset_for_role(self, role):
                return testmodels.SomeItem.objects.none()

        request = self.factory.get("/test")
        self._mock_request(request)
        response = MyObjectTableView.as_view()(request)
        response.render()
        selector = htmls.S(response.content)
        self.assertFalse(selector.exists(".cradmin-searchform"))

    def test_paginate_by_singlepage(self):
        testmodels.SomeItem.objects.bulk_create([testmodels.SomeItem(name=str(x)) for x in range(4)])

        class MyObjectTableView(objecttable.ObjectTableView):
            model = testmodels.SomeItem
            paginate_by = 4

            def get_queryset_for_role(self, role):
                return testmodels.SomeItem.objects.all()

        request = self.factory.get("/test")
        self._mock_request(request)
        response = MyObjectTableView.as_view()(request)
        response.render()
        selector = htmls.S(response.content)
        # selector.one('#cradmin_legacy_contentwrapper').prettyprint()
        self.assertEqual(selector.count("#objecttableview-table>tbody>tr"), 4)
        self.assertFalse(selector.exists("#cradmin_legacy_contentwrapper .pager"))

    def test_paginate_by_firstpage(self):
        testmodels.SomeItem.objects.bulk_create([testmodels.SomeItem(name=str(x)) for x in range(5)])

        class MyObjectTableView(objecttable.ObjectTableView):
            model = testmodels.SomeItem
            paginate_by = 4

            def get_queryset_for_role(self, role):
                return testmodels.SomeItem.objects.all()

        request = self.factory.get("/test")
        self._mock_request(request)
        response = MyObjectTableView.as_view()(request)
        response.render()
        selector = htmls.S(response.content)
        self.assertEqual(selector.count("#objecttableview-table>tbody>tr"), 4)
        self.assertTrue(selector.exists("#cradmin_legacy_contentwrapper .pager"))
        self.assertTrue(selector.exists("#cradmin_legacy_contentwrapper .pager .previous.disabled"))
        self.assertTrue(selector.exists("#cradmin_legacy_contentwrapper .pager .next"))
        self.assertFalse(selector.exists("#cradmin_legacy_contentwrapper .pager .next.disabled"))

    def test_paginate_by_lastpage(self):
        testmodels.SomeItem.objects.bulk_create([testmodels.SomeItem(name=str(x)) for x in range(5)])

        class MyObjectTableView(objecttable.ObjectTableView):
            model = testmodels.SomeItem
            paginate_by = 4

            def get_queryset_for_role(self, role):
                return testmodels.SomeItem.objects.all()

        request = self.factory.get("/test", {"page": 2})
        self._mock_request(request)
        response = MyObjectTableView.as_view()(request)
        response.render()
        selector = htmls.S(response.content)
        self.assertEqual(selector.count("#objecttableview-table>tbody>tr"), 1)
        self.assertTrue(selector.exists("#cradmin_legacy_contentwrapper .pager"))
        self.assertTrue(selector.exists("#cradmin_legacy_contentwrapper .pager .previous"))
        self.assertFalse(selector.exists("#cradmin_legacy_contentwrapper .pager .previous.disabled"))
        self.assertTrue(selector.exists("#cradmin_legacy_contentwrapper .pager .next.disabled"))

    def test_paginate_by_middlepage(self):
        testmodels.SomeItem.objects.bulk_create([testmodels.SomeItem(name=str(x)) for x in range(9)])

        class MyObjectTableView(objecttable.ObjectTableView):
            model = testmodels.SomeItem
            paginate_by = 4

            def get_queryset_for_role(self, role):
                return testmodels.SomeItem.objects.all()

        request = self.factory.get("/test", {"page": 2})
        self._mock_request(request)
        response = MyObjectTableView.as_view()(request)
        response.render()
        selector = htmls.S(response.content)
        # selector.one('#cradmin_legacy_contentwrapper').prettyprint()
        self.assertEqual(selector.count("#objecttableview-table>tbody>tr"), 4)
        self.assertTrue(selector.exists("#cradmin_legacy_contentwrapper .pager"))
        self.assertTrue(selector.exists("#cradmin_legacy_contentwrapper .pager .previous"))
        self.assertTrue(selector.exists("#cradmin_legacy_contentwrapper .pager .next"))
        self.assertFalse(selector.exists("#cradmin_legacy_contentwrapper .pager .previous.disabled"))
        self.assertFalse(selector.exists("#cradmin_legacy_contentwrapper .pager .next.disabled"))

    def test_render_single_simple_column(self):
        testmodels.SomeItem.objects.create(name="Item One")

        class MyObjectTableView(objecttable.ObjectTableView):
            model = testmodels.SomeItem
            columns = ["name"]

            def get_queryset_for_role(self, role):
                return testmodels.SomeItem.objects.all()

        request = self.factory.get("/test")
        self._mock_request(request)
        response = MyObjectTableView.as_view()(request)
        response.render()
        selector = htmls.S(response.content)

        self.assertEqual(selector.count("#objecttableview-table>thead>tr>th"), 1)
        self.assertEqual(
            selector.one("#objecttableview-table>thead>tr>th").alltext_normalized,
            "The name - Ordered descending - Click to order ascending",
        )

        self.assertEqual(selector.count("#objecttableview-table>tbody>tr"), 1)
        self.assertEqual(selector.count("#objecttableview-table>tbody>tr>td"), 1)
        self.assertEqual(selector.one("#objecttableview-table>tbody>tr>td").alltext_normalized, "Item One")

    def test_render_multiple_simple_columns(self):
        testmodels.SomeItem.objects.create(name="Item One", somenumber=10)

        class MyObjectTableView(objecttable.ObjectTableView):
            model = testmodels.SomeItem
            columns = ["name", "somenumber"]

            def get_queryset_for_role(self, role):
                return testmodels.SomeItem.objects.all()

        request = self.factory.get("/test")
        self._mock_request(request)
        response = MyObjectTableView.as_view()(request)
        response.render()
        selector = htmls.S(response.content)

        self.assertEqual(selector.count("#objecttableview-table>thead>tr>th"), 2)
        self.assertEqual(
            selector.one("#objecttableview-table>thead>tr>th:first-child").alltext_normalized,
            "The name - Ordered descending - Click to order ascending",
        )
        self.assertEqual(
            selector.one("#objecttableview-table>thead>tr>th:last-child").alltext_normalized,
            "Somenumber - Ordered descending - Click to order ascending",
        )

        self.assertEqual(selector.count("#objecttableview-table>tbody>tr"), 1)
        self.assertEqual(selector.count("#objecttableview-table>tbody>tr>td"), 2)
        self.assertEqual(selector.one("#objecttableview-table>tbody>tr>td:first-child").alltext_normalized, "Item One")
        self.assertEqual(selector.one("#objecttableview-table>tbody>tr>td:last-child").alltext_normalized, "10")

    def test_render_order_ascending_singlecolumn(self):
        testmodels.SomeItem.objects.create(name="Item A")
        testmodels.SomeItem.objects.create(name="Item B")
        testmodels.SomeItem.objects.create(name="Item C")

        class MyObjectTableView(objecttable.ObjectTableView):
            model = testmodels.SomeItem
            columns = ["name"]

            def get_queryset_for_role(self, role):
                return testmodels.SomeItem.objects.all()

        request = self.factory.get("/test", {"ordering": "a0"})
        self._mock_request(request)
        response = MyObjectTableView.as_view()(request)
        response.render()
        selector = htmls.S(response.content)

        self.assertEqual(selector.count("#objecttableview-table>tbody>tr"), 3)
        self.assertEqual(selector.one("#objecttableview-table>tbody>tr:first-child>td").alltext_normalized, "Item A")
        self.assertEqual(selector.one("#objecttableview-table>tbody>tr:last-child>td").alltext_normalized, "Item C")

        self.assertEqual(
            selector.one("#objecttableview-table>thead>tr>th").alltext_normalized,
            "The name - Ordered ascending - Click to order descending",
        )

    def test_render_order_descending_column(self):
        testmodels.SomeItem.objects.create(name="Item A")
        testmodels.SomeItem.objects.create(name="Item B")
        testmodels.SomeItem.objects.create(name="Item C")

        class MyObjectTableView(objecttable.ObjectTableView):
            model = testmodels.SomeItem
            columns = ["name"]

            def get_queryset_for_role(self, role):
                return testmodels.SomeItem.objects.all()

        request = self.factory.get("/test", {"ordering": "d0"})
        self._mock_request(request)
        response = MyObjectTableView.as_view()(request)
        response.render()
        selector = htmls.S(response.content)
        # selector.one('#cradmin_legacy_contentwrapper thead').prettyprint()

        self.assertEqual(selector.count("#objecttableview-table>tbody>tr"), 3)
        self.assertEqual(selector.one("#objecttableview-table>tbody>tr:first-child>td").alltext_normalized, "Item C")
        self.assertEqual(selector.one("#objecttableview-table>tbody>tr:last-child>td").alltext_normalized, "Item A")

        self.assertEqual(
            selector.one("#objecttableview-table>thead>tr>th").alltext_normalized,
            "The name - Ordered descending - Click to order ascending",
        )

    def test_render_order_multicolumn(self):
        testmodels.SomeItem.objects.create(name="Item A", somenumber=1)
        testmodels.SomeItem.objects.create(name="Item B", somenumber=2)
        testmodels.SomeItem.objects.create(name="Item C", somenumber=2)

        class MyObjectTableView(objecttable.ObjectTableView):
            model = testmodels.SomeItem
            columns = ["name", "somenumber"]

            def get_queryset_for_role(self, role):
                return testmodels.SomeItem.objects.all()

        request = self.factory.get("/test", {"ordering": "a1.d0"})
        self._mock_request(request)
        response = MyObjectTableView.as_view()(request)
        response.render()
        selector = htmls.S(response.content)
        # selector.one('#cradmin_legacy_contentwrapper thead').prettyprint()

        (self.assertEqual(selector.count("#objecttableview-table>thead>tr>th"), 2),)
        self.assertEqual(
            selector.one("#objecttableview-table>thead>tr>th:first-child").alltext_normalized,
            "The name - Ordered descending - Click to order ascending - Ordering priority 2",
        )
        self.assertEqual(
            selector.one("#objecttableview-table>thead>tr>th:last-child").alltext_normalized,
            "Somenumber - Ordered ascending - Click to order descending - Ordering priority 1",
        )

        self.assertEqual(selector.count("#objecttableview-table>tbody>tr"), 3)
        self.assertEqual(
            selector.one("#objecttableview-table>tbody>tr:first-child>td:first-child").alltext_normalized, "Item A"
        )
        self.assertEqual(
            selector.one("#objecttableview-table>tbody>tr:last-child>td:first-child").alltext_normalized, "Item B"
        )

    def test_render_search_nomatch(self):
        testmodels.SomeItem.objects.create(name="Item One")

        class MyObjectTableView(objecttable.ObjectTableView):
            model = testmodels.SomeItem
            columns = ["name"]
            searchfields = ["name"]

            def get_queryset_for_role(self, role):
                return testmodels.SomeItem.objects.all()

        request = self.factory.get("/test", {"search": "Nothing matches this"})
        self._mock_request(request)
        response = MyObjectTableView.as_view()(request)
        response.render()
        selector = htmls.S(response.content)
        self.assertEqual(selector.count("#objecttableview-table>tbody>tr"), 0)

    def test_render_search_match(self):
        testmodels.SomeItem.objects.create(name="Item One")
        testmodels.SomeItem.objects.create(name="Item Two")
        testmodels.SomeItem.objects.create(name="Item Three")

        class MyObjectTableView(objecttable.ObjectTableView):
            model = testmodels.SomeItem
            columns = ["name"]
            searchfields = ["name"]

            def get_queryset_for_role(self, role):
                return testmodels.SomeItem.objects.all()

        request = self.factory.get("/test", {"search": "Item Two"})
        self._mock_request(request)
        response = MyObjectTableView.as_view()(request)
        response.render()
        selector = htmls.S(response.content)

        self.assertEqual(selector.count("#objecttableview-table>tbody>tr"), 1)
        self.assertEqual(selector.one("#objecttableview-table>tbody>tr>td").alltext_normalized, "Item Two")

    def test_show_column_headers(self):
        testmodels.SomeItem.objects.create(name="Item One")

        class MyObjectTableView(objecttable.ObjectTableView):
            model = testmodels.SomeItem
            columns = ["name"]

            def get_queryset_for_role(self, role):
                return testmodels.SomeItem.objects.all()

        request = self.factory.get("/")
        self._mock_request(request)
        response = MyObjectTableView.as_view()(request)
        response.render()
        selector = htmls.S(response.content)

        self.assertTrue(selector.exists("#objecttableview-table>thead"))
        self.assertFalse(selector.exists("#objecttableview-table>thead.sr-only"))

    def test_hide_column_headers(self):
        testmodels.SomeItem.objects.create(name="Item One")

        class MyObjectTableView(objecttable.ObjectTableView):
            model = testmodels.SomeItem
            columns = ["name"]
            hide_column_headers = True

            def get_queryset_for_role(self, role):
                return testmodels.SomeItem.objects.all()

        request = self.factory.get("/")
        self._mock_request(request)
        response = MyObjectTableView.as_view()(request)
        response.render()
        selector = htmls.S(response.content)

        self.assertTrue(selector.exists("#objecttableview-table>thead"))
        self.assertTrue(selector.exists("#objecttableview-table>thead.sr-only"))
