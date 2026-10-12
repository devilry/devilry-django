from django.test import TestCase
from model_bakery import baker

from cradmin_legacy.tests.viewhelpers.cradmin_viewhelpers_testapp.models import FilterTestModel
from cradmin_legacy.viewhelpers import listfilter


class TestSearch(TestCase):
    def test_no_value(self):
        testfilter = listfilter.django.single.textinput.Search(
            slug="mycharfield", modelfields=["mycharfield", "mytextfield"]
        )
        testfilter.set_values(values=[])
        withvalue1 = baker.make("cradmin_viewhelpers_testapp.FilterTestModel", mycharfield="A testvalue")
        withvalue2 = baker.make("cradmin_viewhelpers_testapp.FilterTestModel", mytextfield="Another testvalue")
        emptyvalue = baker.make("cradmin_viewhelpers_testapp.FilterTestModel", mycharfield="")
        nullvalue = baker.make("cradmin_viewhelpers_testapp.FilterTestModel", mycharfield=None)
        self.assertEqual(
            {withvalue1, withvalue2, emptyvalue, nullvalue},
            set(testfilter.filter(queryobject=FilterTestModel.objects.all())),
        )

    def test_matching_single(self):
        testfilter = listfilter.django.single.textinput.Search(
            slug="mycharfield", modelfields=["mycharfield", "mytextfield"]
        )
        testfilter.set_values(values=["Another"])
        baker.make("cradmin_viewhelpers_testapp.FilterTestModel", mycharfield="A testvalue")
        withvalue2 = baker.make("cradmin_viewhelpers_testapp.FilterTestModel", mytextfield="Another testvalue")
        baker.make("cradmin_viewhelpers_testapp.FilterTestModel", mycharfield="")
        baker.make("cradmin_viewhelpers_testapp.FilterTestModel", mycharfield=None)
        self.assertEqual({withvalue2}, set(testfilter.filter(queryobject=FilterTestModel.objects.all())))

    def test_matching_multiple(self):
        testfilter = listfilter.django.single.textinput.Search(
            slug="mycharfield", modelfields=["mycharfield", "mytextfield"]
        )
        testfilter.set_values(values=["testvalue"])
        withvalue1 = baker.make("cradmin_viewhelpers_testapp.FilterTestModel", mycharfield="A testvalue")
        withvalue2 = baker.make("cradmin_viewhelpers_testapp.FilterTestModel", mytextfield="Another testvalue")
        baker.make("cradmin_viewhelpers_testapp.FilterTestModel", mycharfield="")
        baker.make("cradmin_viewhelpers_testapp.FilterTestModel", mycharfield=None)
        self.assertEqual({withvalue1, withvalue2}, set(testfilter.filter(queryobject=FilterTestModel.objects.all())))
