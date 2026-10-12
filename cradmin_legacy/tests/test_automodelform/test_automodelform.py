import datetime

import htmls
from django import test
from django.core.files.base import ContentFile
from model_bakery import baker

from cradmin_legacy import automodelform
from cradmin_legacy.apps.cradmin_imagearchive.tests.helpers import create_image
from cradmin_legacy.tests.test_automodelform.cradmin_automodelform_testapp.models import AutoFormTestModel
from cradmin_legacy import datetimeutils
from cradmin_legacy.python2_compatibility import mock


class TestModelForm(test.TestCase):
    def test_datetime_field_without_default_no_instance(self):
        class MyModelForm(automodelform.ModelForm):
            class Meta:
                model = AutoFormTestModel
                fields = ["datetimefield_without_default"]

        selector = htmls.S(MyModelForm().as_ul())
        self.assertEqual("", selector.one('input[type="text"][name="datetimefield_without_default"]').get("value", ""))
        self.assertTrue(selector.exists(".cradmin-legacy-datepicker-triggerbutton"))

    def test_datetime_field_without_default_with_instance(self):
        class MyModelForm(automodelform.ModelForm):
            class Meta:
                model = AutoFormTestModel
                fields = ["datetimefield_without_default"]

        autoformtestmodelobject = baker.make(
            "cradmin_automodelform_testapp.AutoFormTestModel",
            datetimefield_without_default=datetimeutils.default_timezone_datetime(2015, 12, 24, 12, 0, 0),
        )
        selector = htmls.S(MyModelForm(instance=autoformtestmodelobject).as_ul())
        self.assertEqual(
            "2015-12-24 12:00:00", selector.one('input[type="text"][name="datetimefield_without_default"]')["value"]
        )
        self.assertTrue(selector.exists(".cradmin-legacy-datepicker-triggerbutton"))

    def test_datetime_field_with_default_no_instance(self):
        class MyModelForm(automodelform.ModelForm):
            class Meta:
                model = AutoFormTestModel
                fields = ["datetimefield_with_default"]

        selector = htmls.S(MyModelForm().as_ul())
        self.assertNotEqual("", selector.one('input[type="text"][name="datetimefield_with_default"]')["value"])
        self.assertTrue(selector.exists(".cradmin-legacy-datepicker-triggerbutton"))

    def test_datetime_field_with_default_with_instance(self):
        class MyModelForm(automodelform.ModelForm):
            class Meta:
                model = AutoFormTestModel
                fields = ["datetimefield_with_default"]

        autoformtestmodelobject = baker.make(
            "cradmin_automodelform_testapp.AutoFormTestModel",
            datetimefield_with_default=datetimeutils.default_timezone_datetime(2015, 12, 24, 12, 0, 0),
        )
        selector = htmls.S(MyModelForm(instance=autoformtestmodelobject).as_ul())
        self.assertEqual(
            "2015-12-24 12:00:00", selector.one('input[type="text"][name="datetimefield_with_default"]')["value"]
        )
        self.assertTrue(selector.exists(".cradmin-legacy-datepicker-triggerbutton"))

    def test_date_field_without_default_no_instance(self):
        class MyModelForm(automodelform.ModelForm):
            class Meta:
                model = AutoFormTestModel
                fields = ["datefield_without_default"]

        selector = htmls.S(MyModelForm().as_ul())
        self.assertEqual("", selector.one('input[type="text"][name="datefield_without_default"]').get("value", ""))
        self.assertTrue(selector.exists(".cradmin-legacy-datepicker-triggerbutton"))

    def test_date_field_without_default_with_instance(self):
        class MyModelForm(automodelform.ModelForm):
            class Meta:
                model = AutoFormTestModel
                fields = ["datefield_without_default"]

        autoformtestmodelobject = baker.make(
            "cradmin_automodelform_testapp.AutoFormTestModel", datefield_without_default=datetime.date(2015, 12, 24)
        )
        selector = htmls.S(MyModelForm(instance=autoformtestmodelobject).as_ul())
        self.assertEqual("2015-12-24", selector.one('input[type="text"][name="datefield_without_default"]')["value"])
        self.assertTrue(selector.exists(".cradmin-legacy-datepicker-triggerbutton"))

    def test_date_field_with_default_no_instance(self):
        class MyModelForm(automodelform.ModelForm):
            class Meta:
                model = AutoFormTestModel
                fields = ["datefield_with_default"]

        selector = htmls.S(MyModelForm().as_ul())
        self.assertNotEqual("", selector.one('input[type="text"][name="datefield_with_default"]')["value"])
        self.assertTrue(selector.exists(".cradmin-legacy-datepicker-triggerbutton"))

    def test_date_field_with_default_with_instance(self):
        class MyModelForm(automodelform.ModelForm):
            class Meta:
                model = AutoFormTestModel
                fields = ["datefield_with_default"]

        autoformtestmodelobject = baker.make(
            "cradmin_automodelform_testapp.AutoFormTestModel", datefield_with_default=datetime.date(2015, 12, 24)
        )
        selector = htmls.S(MyModelForm(instance=autoformtestmodelobject).as_ul())
        self.assertEqual("2015-12-24", selector.one('input[type="text"][name="datefield_with_default"]')["value"])
        self.assertTrue(selector.exists(".cradmin-legacy-datepicker-triggerbutton"))

    def test_file_field_without_default_no_instance(self):
        class MyModelForm(automodelform.ModelForm):
            class Meta:
                model = AutoFormTestModel
                fields = ["filefield"]

        selector = htmls.S(MyModelForm().as_ul())
        self.assertTrue(selector.exists('input[type="file"][name="filefield"]'))
        self.assertTrue(selector.exists(".cradmin-legacy-filewidget"))

    def test_file_field_without_default_with_instance(self):
        class MyModelForm(automodelform.ModelForm):
            class Meta:
                model = AutoFormTestModel
                fields = ["filefield"]

        autoformtestmodelobject = baker.make("cradmin_automodelform_testapp.AutoFormTestModel", filefield="test.txt")
        selector = htmls.S(MyModelForm(instance=autoformtestmodelobject).as_ul())
        self.assertTrue(selector.exists('input[type="file"][name="filefield"]'))
        self.assertTrue(selector.exists(".cradmin-legacy-filewidget"))

    def test_image_field_without_default_no_instance(self):
        class MyModelForm(automodelform.ModelForm):
            class Meta:
                model = AutoFormTestModel
                fields = ["imagefield"]

        selector = htmls.S(MyModelForm(view=mock.MagicMock()).as_ul())
        self.assertTrue(selector.exists('input[type="file"][name="imagefield"]'))
        self.assertTrue(selector.exists(".cradmin-legacy-imagewidget"))

    def test_image_field_without_default_with_instance(self):
        class MyModelForm(automodelform.ModelForm):
            class Meta:
                model = AutoFormTestModel
                fields = ["imagefield"]

        autoformtestmodelobject = baker.make("cradmin_automodelform_testapp.AutoFormTestModel")
        testimage = create_image(200, 100)
        autoformtestmodelobject.imagefield.save("testimage.png", ContentFile(testimage))

        mockview = mock.MagicMock()
        mockview.request.build_absolute_uri.return_value = "testimage.png"

        with self.settings(CRADMIN_LEGACY_IMAGEUTILS_IMAGETYPE_MAP={}):
            selector = htmls.S(MyModelForm(view=mockview, instance=autoformtestmodelobject).as_ul())
        self.assertTrue(selector.exists('input[type="file"][name="imagefield"]'))
        self.assertTrue(selector.exists(".cradmin-legacy-imagewidget"))
