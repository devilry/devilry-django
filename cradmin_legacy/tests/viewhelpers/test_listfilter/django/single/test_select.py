from django.test import TestCase
from model_bakery import baker

from cradmin_legacy import datetimeutils
from cradmin_legacy.python2_compatibility import mock
from cradmin_legacy.tests.viewhelpers.cradmin_viewhelpers_testapp.models import FilterTestModel
from cradmin_legacy.viewhelpers import listfilter


class TestBoolean(TestCase):
    def test_no_value(self):
        testfilter = listfilter.django.single.select.Boolean(slug="mycharfield")
        testfilter.set_values(values=[])
        withvalue = baker.make("cradmin_viewhelpers_testapp.FilterTestModel", mycharfield="A testvalue")
        emptyvalue = baker.make("cradmin_viewhelpers_testapp.FilterTestModel", mycharfield="")
        nullvalue = baker.make("cradmin_viewhelpers_testapp.FilterTestModel", mycharfield=None)
        self.assertEqual(
            {withvalue, emptyvalue, nullvalue}, set(testfilter.filter(queryobject=FilterTestModel.objects.all()))
        )

    def test_invalid_value(self):
        testfilter = listfilter.django.single.select.Boolean(slug="mycharfield")
        testfilter.set_values(values=["invalidstuff"])
        withvalue = baker.make("cradmin_viewhelpers_testapp.FilterTestModel", mycharfield="A testvalue")
        emptyvalue = baker.make("cradmin_viewhelpers_testapp.FilterTestModel", mycharfield="")
        nullvalue = baker.make("cradmin_viewhelpers_testapp.FilterTestModel", mycharfield=None)
        self.assertEqual(
            {withvalue, emptyvalue, nullvalue}, set(testfilter.filter(queryobject=FilterTestModel.objects.all()))
        )

    def test_false_booleanfield(self):
        testfilter = listfilter.django.single.select.Boolean(slug="mybooleanfield")
        testfilter.set_values(values=["false"])
        baker.make("cradmin_viewhelpers_testapp.FilterTestModel", mybooleanfield=True)
        falsevalue = baker.make("cradmin_viewhelpers_testapp.FilterTestModel", mybooleanfield=False)
        self.assertEqual({falsevalue}, set(testfilter.filter(queryobject=FilterTestModel.objects.all())))

    def test_true_booleanfield(self):
        testfilter = listfilter.django.single.select.Boolean(slug="mybooleanfield")
        testfilter.set_values(values=["true"])
        truevalue = baker.make("cradmin_viewhelpers_testapp.FilterTestModel", mybooleanfield=True)
        baker.make("cradmin_viewhelpers_testapp.FilterTestModel", mybooleanfield=False)
        self.assertEqual({truevalue}, set(testfilter.filter(queryobject=FilterTestModel.objects.all())))


class TestIsNotNull(TestCase):
    def test_false(self):
        testfilter = listfilter.django.single.select.IsNotNull(slug="myintnullfield")
        testfilter.set_values(values=["false"])
        baker.make("cradmin_viewhelpers_testapp.FilterTestModel", myintnullfield=10)
        nullvalue = baker.make("cradmin_viewhelpers_testapp.FilterTestModel", myintnullfield=None)
        self.assertEqual({nullvalue}, set(testfilter.filter(queryobject=FilterTestModel.objects.all())))

    def test_true(self):
        testfilter = listfilter.django.single.select.IsNotNull(slug="myintnullfield")
        testfilter.set_values(values=["true"])
        withvalue = baker.make("cradmin_viewhelpers_testapp.FilterTestModel", myintnullfield=10)
        baker.make("cradmin_viewhelpers_testapp.FilterTestModel", myintnullfield=None)
        self.assertEqual({withvalue}, set(testfilter.filter(queryobject=FilterTestModel.objects.all())))

    def test_true_zero(self):
        testfilter = listfilter.django.single.select.IsNotNull(slug="myintnullfield")
        testfilter.set_values(values=["true"])
        withvalue = baker.make("cradmin_viewhelpers_testapp.FilterTestModel", myintnullfield=0)
        baker.make("cradmin_viewhelpers_testapp.FilterTestModel", myintnullfield=None)
        self.assertEqual({withvalue}, set(testfilter.filter(queryobject=FilterTestModel.objects.all())))


class TestDateTime(TestCase):
    def test_no_value(self):
        testfilter = listfilter.django.single.select.DateTime(slug="mydatetimefield")
        testfilter.set_values(values=[])
        testitem = baker.make("cradmin_viewhelpers_testapp.FilterTestModel")
        self.assertEqual({testitem}, set(testfilter.filter(queryobject=FilterTestModel.objects.all())))

    def test_invalid_value(self):
        testfilter = listfilter.django.single.select.DateTime(slug="mydatetimefield")
        testfilter.set_values(values=["invalidstuff"])
        testitem = baker.make("cradmin_viewhelpers_testapp.FilterTestModel")
        self.assertEqual({testitem}, set(testfilter.filter(queryobject=FilterTestModel.objects.all())))

    def test_today_nomatch(self):
        testfilter = listfilter.django.single.select.DateTime(slug="mydatetimefield")
        testfilter.set_values(values=["today"])
        baker.make(
            "cradmin_viewhelpers_testapp.FilterTestModel",
            mydatetimefield=datetimeutils.default_timezone_datetime(2015, 1, 1),
        )
        with mock.patch(
            "cradmin_legacy.viewhelpers.listfilter.basefilters.single.abstractselect.timezone.now",
            lambda: datetimeutils.default_timezone_datetime(2015, 1, 2),
        ):
            self.assertFalse(testfilter.filter(queryobject=FilterTestModel.objects.all()).exists())

    def test_today_match(self):
        testfilter = listfilter.django.single.select.DateTime(slug="mydatetimefield")
        testfilter.set_values(values=["today"])
        testitem = baker.make(
            "cradmin_viewhelpers_testapp.FilterTestModel",
            mydatetimefield=datetimeutils.default_timezone_datetime(2015, 1, 1),
        )
        with mock.patch(
            "cradmin_legacy.viewhelpers.listfilter.basefilters.single.abstractselect.timezone.now",
            lambda: datetimeutils.default_timezone_datetime(2015, 1, 1, 12, 30),
        ):
            self.assertEqual({testitem}, set(testfilter.filter(queryobject=FilterTestModel.objects.all())))

    def test_yesterday_nomatch(self):
        testfilter = listfilter.django.single.select.DateTime(slug="mydatetimefield")
        testfilter.set_values(values=["yesterday"])
        baker.make(
            "cradmin_viewhelpers_testapp.FilterTestModel",
            mydatetimefield=datetimeutils.default_timezone_datetime(2015, 1, 10),
        )
        with mock.patch(
            "cradmin_legacy.viewhelpers.listfilter.basefilters.single.abstractselect.timezone.now",
            lambda: datetimeutils.default_timezone_datetime(2015, 1, 12),
        ):
            self.assertFalse(testfilter.filter(queryobject=FilterTestModel.objects.all()).exists())

    def test_yesterday_match(self):
        testfilter = listfilter.django.single.select.DateTime(slug="mydatetimefield")
        testfilter.set_values(values=["yesterday"])
        testitem = baker.make(
            "cradmin_viewhelpers_testapp.FilterTestModel",
            mydatetimefield=datetimeutils.default_timezone_datetime(2015, 1, 10),
        )
        with mock.patch(
            "cradmin_legacy.viewhelpers.listfilter.basefilters.single.abstractselect.timezone.now",
            lambda: datetimeutils.default_timezone_datetime(2015, 1, 11, 12, 30),
        ):
            self.assertEqual({testitem}, set(testfilter.filter(queryobject=FilterTestModel.objects.all())))

    def test_last_seven_days_nomatch(self):
        testfilter = listfilter.django.single.select.DateTime(slug="mydatetimefield")
        testfilter.set_values(values=["last_seven_days"])
        baker.make(
            "cradmin_viewhelpers_testapp.FilterTestModel",
            mydatetimefield=datetimeutils.default_timezone_datetime(2015, 1, 2),
        )
        with mock.patch(
            "cradmin_legacy.viewhelpers.listfilter.basefilters.single.abstractselect.timezone.now",
            lambda: datetimeutils.default_timezone_datetime(2015, 1, 10, 12, 30),
        ):
            self.assertFalse(testfilter.filter(queryobject=FilterTestModel.objects.all()).exists())

    def test_last_seven_days_match(self):
        testfilter = listfilter.django.single.select.DateTime(slug="mydatetimefield")
        testfilter.set_values(values=["last_seven_days"])
        testitem = baker.make(
            "cradmin_viewhelpers_testapp.FilterTestModel",
            mydatetimefield=datetimeutils.default_timezone_datetime(2015, 1, 3),
        )
        with mock.patch(
            "cradmin_legacy.viewhelpers.listfilter.basefilters.single.abstractselect.timezone.now",
            lambda: datetimeutils.default_timezone_datetime(2015, 1, 10, 12, 30),
        ):
            self.assertEqual({testitem}, set(testfilter.filter(queryobject=FilterTestModel.objects.all())))

    def test_this_week_nomatch(self):
        testfilter = listfilter.django.single.select.DateTime(slug="mydatetimefield")
        testfilter.set_values(values=["this_week"])
        baker.make(
            "cradmin_viewhelpers_testapp.FilterTestModel",
            mydatetimefield=datetimeutils.default_timezone_datetime(2015, 11, 29),
        )
        baker.make(
            "cradmin_viewhelpers_testapp.FilterTestModel",
            mydatetimefield=datetimeutils.default_timezone_datetime(2015, 12, 7),
        )
        with mock.patch(
            "cradmin_legacy.viewhelpers.listfilter.basefilters.single.abstractselect.timezone.now",
            lambda: datetimeutils.default_timezone_datetime(2015, 12, 1, 12, 30),
        ):
            self.assertFalse(testfilter.filter(queryobject=FilterTestModel.objects.all()).exists())

    def test_this_week_match(self):
        testfilter = listfilter.django.single.select.DateTime(slug="mydatetimefield")
        testfilter.set_values(values=["this_week"])
        start_of_week = baker.make(
            "cradmin_viewhelpers_testapp.FilterTestModel",
            mydatetimefield=datetimeutils.default_timezone_datetime(2015, 11, 30),
        )
        end_of_week = baker.make(
            "cradmin_viewhelpers_testapp.FilterTestModel",
            mydatetimefield=datetimeutils.default_timezone_datetime(2015, 12, 6, 23),
        )
        with mock.patch(
            "cradmin_legacy.viewhelpers.listfilter.basefilters.single.abstractselect.timezone.now",
            lambda: datetimeutils.default_timezone_datetime(2015, 12, 1, 12, 30),
        ):
            self.assertEqual(
                {start_of_week, end_of_week}, set(testfilter.filter(queryobject=FilterTestModel.objects.all()))
            )

    def test_this_month_nomatch(self):
        testfilter = listfilter.django.single.select.DateTime(slug="mydatetimefield")
        testfilter.set_values(values=["this_month"])
        baker.make(
            "cradmin_viewhelpers_testapp.FilterTestModel",
            mydatetimefield=datetimeutils.default_timezone_datetime(2015, 11, 29),
        )
        baker.make(
            "cradmin_viewhelpers_testapp.FilterTestModel",
            mydatetimefield=datetimeutils.default_timezone_datetime(2016, 1, 1),
        )
        with mock.patch(
            "cradmin_legacy.viewhelpers.listfilter.basefilters.single.abstractselect.timezone.now",
            lambda: datetimeutils.default_timezone_datetime(2015, 12, 7, 12, 30),
        ):
            self.assertFalse(testfilter.filter(queryobject=FilterTestModel.objects.all()).exists())

    def test_this_month_match(self):
        testfilter = listfilter.django.single.select.DateTime(slug="mydatetimefield")
        testfilter.set_values(values=["this_month"])
        start_of_month = baker.make(
            "cradmin_viewhelpers_testapp.FilterTestModel",
            mydatetimefield=datetimeutils.default_timezone_datetime(2015, 12, 1),
        )
        middle_of_month = baker.make(
            "cradmin_viewhelpers_testapp.FilterTestModel",
            mydatetimefield=datetimeutils.default_timezone_datetime(2015, 12, 24),
        )
        end_of_month = baker.make(
            "cradmin_viewhelpers_testapp.FilterTestModel",
            mydatetimefield=datetimeutils.default_timezone_datetime(2015, 12, 31, 23),
        )
        with mock.patch(
            "cradmin_legacy.viewhelpers.listfilter.basefilters.single.abstractselect.timezone.now",
            lambda: datetimeutils.default_timezone_datetime(2015, 12, 7, 12, 30),
        ):
            self.assertEqual(
                {start_of_month, middle_of_month, end_of_month},
                set(testfilter.filter(queryobject=FilterTestModel.objects.all())),
            )

    def test_this_year_nomatch(self):
        testfilter = listfilter.django.single.select.DateTime(slug="mydatetimefield")
        testfilter.set_values(values=["this_year"])
        baker.make(
            "cradmin_viewhelpers_testapp.FilterTestModel",
            mydatetimefield=datetimeutils.default_timezone_datetime(2014, 12, 31),
        )
        baker.make(
            "cradmin_viewhelpers_testapp.FilterTestModel",
            mydatetimefield=datetimeutils.default_timezone_datetime(2016, 1, 1),
        )
        with mock.patch(
            "cradmin_legacy.viewhelpers.listfilter.basefilters.single.abstractselect.timezone.now",
            lambda: datetimeutils.default_timezone_datetime(2015, 12, 24),
        ):
            self.assertFalse(testfilter.filter(queryobject=FilterTestModel.objects.all()).exists())

    def test_this_year_match(self):
        testfilter = listfilter.django.single.select.DateTime(slug="mydatetimefield")
        testfilter.set_values(values=["this_year"])
        start_of_year = baker.make(
            "cradmin_viewhelpers_testapp.FilterTestModel",
            mydatetimefield=datetimeutils.default_timezone_datetime(2015, 1, 1),
        )
        middle_of_year = baker.make(
            "cradmin_viewhelpers_testapp.FilterTestModel",
            mydatetimefield=datetimeutils.default_timezone_datetime(2015, 6, 1),
        )
        end_of_year = baker.make(
            "cradmin_viewhelpers_testapp.FilterTestModel",
            mydatetimefield=datetimeutils.default_timezone_datetime(2015, 12, 31, 23),
        )
        with mock.patch(
            "cradmin_legacy.viewhelpers.listfilter.basefilters.single.abstractselect.timezone.now",
            lambda: datetimeutils.default_timezone_datetime(2015, 12, 24),
        ):
            self.assertEqual(
                {start_of_year, middle_of_year, end_of_year},
                set(testfilter.filter(queryobject=FilterTestModel.objects.all())),
            )


class TestNullDateTime(TestCase):
    def test_is_null(self):
        testfilter = listfilter.django.single.select.NullDateTime(slug="mynulldatetimefield")
        testfilter.set_values(values=["is_null"])
        baker.make(
            "cradmin_viewhelpers_testapp.FilterTestModel",
            mynulldatetimefield=datetimeutils.default_timezone_datetime(2014, 12, 31),
        )
        isnull = baker.make("cradmin_viewhelpers_testapp.FilterTestModel", mynulldatetimefield=None)
        self.assertEqual({isnull}, set(testfilter.filter(queryobject=FilterTestModel.objects.all())))

    def test_is_not_null(self):
        testfilter = listfilter.django.single.select.NullDateTime(slug="mynulldatetimefield")
        testfilter.set_values(values=["is_not_null"])
        isnotnull = baker.make(
            "cradmin_viewhelpers_testapp.FilterTestModel",
            mynulldatetimefield=datetimeutils.default_timezone_datetime(2014, 12, 31),
        )
        baker.make("cradmin_viewhelpers_testapp.FilterTestModel", mynulldatetimefield=None)
        self.assertEqual({isnotnull}, set(testfilter.filter(queryobject=FilterTestModel.objects.all())))


class TestOrderBy(TestCase):
    def test_invalid_value(self):
        class OrderByFilter(listfilter.django.single.select.AbstractOrderBy):
            def get_ordering_options(self):
                return []

        testfilter = OrderByFilter(slug="orderby")
        testfilter.set_values(values=["invalidstuff"])
        testitem = baker.make("cradmin_viewhelpers_testapp.FilterTestModel")
        self.assertEqual({testitem}, set(testfilter.filter(queryobject=FilterTestModel.objects.all())))

    def test_no_value_defaults_to_the_empty_value(self):
        class OrderByFilter(listfilter.django.single.select.AbstractOrderBy):
            def get_ordering_options(self):
                return [
                    (
                        "",
                        {
                            "label": "mylabel",
                            "order_by": ["mydatetimefield"],
                        },
                    ),
                ]

        testfilter = OrderByFilter(slug="orderby")
        testfilter.set_values(values=[])
        testitem2 = baker.make(
            "cradmin_viewhelpers_testapp.FilterTestModel",
            mydatetimefield=datetimeutils.default_timezone_datetime(2016, 1, 2),
        )
        testitem1 = baker.make(
            "cradmin_viewhelpers_testapp.FilterTestModel",
            mydatetimefield=datetimeutils.default_timezone_datetime(2015, 1, 2),
        )
        self.assertEqual([testitem1, testitem2], list(testfilter.filter(queryobject=FilterTestModel.objects.all())))

    def test_nondefault_value(self):
        class OrderByFilter(listfilter.django.single.select.AbstractOrderBy):
            def get_ordering_options(self):
                return [
                    (
                        "",
                        {
                            "label": "asc",
                            "order_by": ["mydatetimefield"],
                        },
                    ),
                    (
                        "desc",
                        {
                            "label": "desc",
                            "order_by": ["-mydatetimefield"],
                        },
                    ),
                ]

        testfilter = OrderByFilter(slug="orderby")
        testfilter.set_values(values=["desc"])
        testitem2 = baker.make(
            "cradmin_viewhelpers_testapp.FilterTestModel",
            mydatetimefield=datetimeutils.default_timezone_datetime(2016, 1, 2),
        )
        testitem1 = baker.make(
            "cradmin_viewhelpers_testapp.FilterTestModel",
            mydatetimefield=datetimeutils.default_timezone_datetime(2015, 1, 2),
        )
        self.assertEqual([testitem2, testitem1], list(testfilter.filter(queryobject=FilterTestModel.objects.all())))
