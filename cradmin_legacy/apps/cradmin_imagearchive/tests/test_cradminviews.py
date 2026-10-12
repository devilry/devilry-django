import htmls
from django.core.files.base import ContentFile
from django.test import RequestFactory, TestCase
from model_bakery import baker

from cradmin_legacy import cradmin_testhelpers
from cradmin_legacy.apps.cradmin_imagearchive import cradminviews
from cradmin_legacy.apps.cradmin_imagearchive.models import ArchiveImage
from cradmin_legacy.apps.cradmin_temporaryfileuploadstore.models import (
    TemporaryFile,
    TemporaryFileCollection,
)
from cradmin_legacy.cradmin_legacy_testapp.models import TstRole
from cradmin_legacy.python2_compatibility import mock
from cradmin_legacy.tests.helpers import create_user

from .helpers import create_image


def _create_single_file_temporaryfilecollection(user, filename="testfile.png", image=None):
    if image:
        testimage = image
    else:
        testimage = create_image(200, 100)
    collection = TemporaryFileCollection.objects.create(user=user)
    temporaryfile = TemporaryFile(collection=collection, filename=filename)
    temporaryfile.file.save(filename, ContentFile(testimage))
    return collection


class TestUpdateView(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.role = TstRole.objects.create()
        self.archiveimage = ArchiveImage.objects.create(
            role=self.role, name="Original name", description="Original description"
        )
        self.testimage = create_image(200, 100)
        self.archiveimage.image.save("testimage.png", ContentFile(self.testimage))
        self.testuser = create_user("testuser")

    def test_get_render(self):
        request = self.factory.get("/test")
        request.cradmin_instance = mock.MagicMock()
        request.cradmin_role = self.role

        response = cradminviews.ArchiveImageUpdateView.as_view()(request, pk=self.archiveimage.pk)
        self.assertEqual(response.status_code, 200)
        response.render()
        selector = htmls.S(response.content)
        self.assertTrue(selector.exists("textarea#id_description"))

    def test_post_ok(self):
        request = self.factory.post(
            "/test",
            {
                # 'name': 'Updated name',
                "description": "Updated description"
            },
        )
        request.cradmin_instance = mock.MagicMock()
        request.cradmin_app = mock.MagicMock()
        request.cradmin_app.reverse_appurl.return_value = "/success"
        request.cradmin_role = self.role
        request._messages = mock.MagicMock()

        self.assertEqual(ArchiveImage.objects.count(), 1)
        response = cradminviews.ArchiveImageUpdateView.as_view()(request, pk=self.archiveimage.pk)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/success")
        self.assertEqual(ArchiveImage.objects.count(), 1)
        updated_image = ArchiveImage.objects.first()
        self.assertEqual(updated_image.image.read(), self.testimage)
        # self.assertEqual(updated_image.name, 'Updated name')
        self.assertEqual(updated_image.description, "Updated description")


class TestArchiveImagesListView(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = cradminviews.ArchiveImagesListView

    def test_no_archive_images(self):
        mockresponse = self.mock_http200_getrequest_htmls(
            requestuser=create_user("testuser"), cradmin_role=baker.make("cradmin_legacy_testapp.TstRole")
        )
        self.assertEqual(
            mockresponse.selector.one("#objecttableview-no-items-message").alltext_normalized, "No archive images"
        )

    def test_single_archive_image_sanity(self):
        testrole = baker.make("cradmin_legacy_testapp.TstRole")
        baker.make("cradmin_imagearchive.ArchiveImage", name="Test image", description="", role=testrole)
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=create_user("testuser"), cradmin_role=testrole)
        self.assertFalse(mockresponse.selector.exists("#objecttableview-no-items-message"))
        self.assertEqual(mockresponse.selector.count("#objecttableview-table tbody tr"), 1)

    def test_only_owned_by_role(self):
        testrole = baker.make("cradmin_legacy_testapp.TstRole")
        other_role = baker.make("cradmin_legacy_testapp.TstRole")
        baker.make("cradmin_imagearchive.ArchiveImage", name="Test image", description="", role=other_role)
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=create_user("testuser"), cradmin_role=testrole)
        self.assertTrue(mockresponse.selector.exists("#objecttableview-no-items-message"))

    def test_render_single_archive_image_no_description(self):
        testrole = baker.make("cradmin_legacy_testapp.TstRole")
        baker.make("cradmin_imagearchive.ArchiveImage", name="Test image", description="", role=testrole)
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=create_user("testuser"), cradmin_role=testrole)
        self.assertEqual(
            mockresponse.selector.one(
                "#objecttableview-table tbody tr td:last-child .objecttable-cellvalue"
            ).alltext_normalized,
            "Test image",
        )
        self.assertEqual(
            mockresponse.selector.one("#objecttableview-table tbody tr td:last-child .btn-default").alltext_normalized,
            "Set a description",
        )

    def test_render_single_archive_image_has_description(self):
        testrole = baker.make("cradmin_legacy_testapp.TstRole")
        baker.make(
            "cradmin_imagearchive.ArchiveImage", name="Test image", description="Test description", role=testrole
        )
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=create_user("testuser"), cradmin_role=testrole)
        self.assertEqual(
            mockresponse.selector.one(
                "#objecttableview-table tbody tr td:last-child .objecttable-cellvalue"
            ).alltext_normalized,
            "Test description",
        )
        self.assertEqual(
            mockresponse.selector.one("#objecttableview-table tbody tr td:last-child .btn-default").alltext_normalized,
            "Edit description",
        )

    def test_uploadform_get_render(self):
        testrole = baker.make("cradmin_legacy_testapp.TstRole")
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=create_user("testuser"), cradmin_role=testrole)
        self.assertEqual(mockresponse.response.status_code, 200)
        self.assertTrue(mockresponse.selector.exists("#cradmin_legacy_imagearchive_bulkadd_form"))
        self.assertTrue(mockresponse.selector.exists("input[type=hidden][name=filecollectionid]"))
        self.assertTrue(mockresponse.selector.exists("#div_id_filecollectionid"))

    def test_uploadform_post_no_filecollectionid(self):
        self.assertEqual(ArchiveImage.objects.count(), 0)
        testrole = baker.make("cradmin_legacy_testapp.TstRole")
        mockresponse = self.mock_http200_postrequest_htmls(requestuser=create_user("testuser"), cradmin_role=testrole)
        self.assertTrue(mockresponse.selector.exists("#div_id_filecollectionid.has-error"))
        self.assertIn(
            "You must upload at least one image.",
            mockresponse.selector.one("#div_id_filecollectionid").alltext_normalized,
        )

    def test_uploadform_post_single_image(self):
        testuser = create_user("testuser")
        testimage = create_image(200, 100)
        collection = TemporaryFileCollection.objects.create(user=testuser)
        temporaryfile = TemporaryFile(collection=collection, filename="testfile.png")
        temporaryfile.file.save("testfile.png", ContentFile(testimage))

        testrole = baker.make("cradmin_legacy_testapp.TstRole")
        cradmin_app = mock.MagicMock()
        cradmin_app.reverse_appurl.return_value = "/success"
        self.assertEqual(ArchiveImage.objects.count(), 0)
        mockresponse = self.mock_http302_postrequest(
            requestuser=testuser,
            cradmin_role=testrole,
            cradmin_app=cradmin_app,
            requestkwargs={"data": {"filecollectionid": collection.id}},
        )

        self.assertEqual(mockresponse.response["Location"], "/success")
        self.assertEqual(ArchiveImage.objects.count(), 1)
        created_image = ArchiveImage.objects.first()
        created_image.image.open()
        self.assertEqual(created_image.image.read(), testimage)
        created_image.image.close()
        self.assertEqual(created_image.name, "testfile.png")
        self.assertEqual(created_image.description, "")

    def test_uploadform_post_deletes_collection(self):
        testuser = create_user("testuser")
        testimage = create_image(200, 100)
        collection = TemporaryFileCollection.objects.create(user=testuser)
        temporaryfile = TemporaryFile(collection=collection, filename="testfile.png")
        temporaryfile.file.save("testfile.png", ContentFile(testimage))

        testrole = baker.make("cradmin_legacy_testapp.TstRole")
        self.mock_http302_postrequest(
            requestuser=testuser, cradmin_role=testrole, requestkwargs={"data": {"filecollectionid": collection.id}}
        )
        self.assertFalse(TemporaryFileCollection.objects.filter(id=collection.id).exists())

    def test_uploadform_post_multiple_images(self):
        testuser = create_user("testuser")
        testimage1 = create_image(200, 100)
        testimage2 = create_image(100, 100)
        collection = TemporaryFileCollection.objects.create(user=testuser)
        temporaryfile = TemporaryFile(collection=collection, filename="testfile1.png")
        temporaryfile.file.save("testfile1.png", ContentFile(testimage1))
        temporaryfile = TemporaryFile(collection=collection, filename="testfile2.png")
        temporaryfile.file.save("testfile2.png", ContentFile(testimage2))

        testrole = baker.make("cradmin_legacy_testapp.TstRole")
        cradmin_app = mock.MagicMock()
        cradmin_app.reverse_appurl.return_value = "/success"

        self.assertEqual(ArchiveImage.objects.count(), 0)
        mockresponse = self.mock_http302_postrequest(
            requestuser=testuser,
            cradmin_role=testrole,
            cradmin_app=cradmin_app,
            requestkwargs={"data": {"filecollectionid": collection.id}},
        )
        self.assertEqual(mockresponse.response["Location"], "/success")
        self.assertEqual(ArchiveImage.objects.count(), 2)
        created_images = ArchiveImage.objects.order_by("name")

        for image in created_images:
            image.image.open()

        self.assertEqual(created_images[0].image.read(), testimage1)
        self.assertEqual(created_images[0].name, "testfile1.png")
        self.assertEqual(created_images[0].description, "")

        self.assertEqual(created_images[1].image.read(), testimage2)
        self.assertEqual(created_images[1].name, "testfile2.png")
        self.assertEqual(created_images[1].description, "")

        for image in created_images:
            image.image.close()

    def test_uploadform_post_sets_file_size(self):
        testuser = create_user("testuser")
        testimage = create_image(200, 100)
        collection = TemporaryFileCollection.objects.create(user=testuser)
        temporaryfile = TemporaryFile(collection=collection, filename="testfile.png")
        temporaryfile.file.save("testfile.png", ContentFile(testimage))

        testrole = baker.make("cradmin_legacy_testapp.TstRole")
        self.mock_http302_postrequest(
            requestuser=testuser, cradmin_role=testrole, requestkwargs={"data": {"filecollectionid": collection.id}}
        )
        created_image = ArchiveImage.objects.first()
        self.assertEqual(len(testimage), created_image.file_size)


class TestArchiveImagesSingleSelectView(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = cradminviews.ArchiveImagesSingleSelectView

    def test_no_archive_images(self):
        mockresponse = self.mock_http200_getrequest_htmls(
            requestuser=create_user("testuser"), cradmin_role=baker.make("cradmin_legacy_testapp.TstRole")
        )
        self.assertEqual(
            mockresponse.selector.one("#objecttableview-no-items-message").alltext_normalized, "No archive images"
        )

    def test_single_archive_image_sanity(self):
        testrole = baker.make("cradmin_legacy_testapp.TstRole")
        archiveimage = baker.make("cradmin_imagearchive.ArchiveImage", role=testrole)
        archiveimage.image.save("testimage.png", ContentFile(create_image(200, 100)))

        mockresponse = self.mock_http200_getrequest_htmls(
            requestuser=create_user("testuser"),
            cradmin_role=testrole,
            requestkwargs={"data": {"foreignkey_select_fieldid": "testfield"}},
        )
        self.assertFalse(mockresponse.selector.exists("#objecttableview-no-items-message"))
        self.assertEqual(mockresponse.selector.count("#objecttableview-table tbody tr"), 1)

    def test_only_owned_by_role(self):
        testrole = baker.make("cradmin_legacy_testapp.TstRole")
        other_role = baker.make("cradmin_legacy_testapp.TstRole")
        baker.make("cradmin_imagearchive.ArchiveImage", name="Test image", description="", role=other_role)
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=create_user("testuser"), cradmin_role=testrole)
        self.assertTrue(mockresponse.selector.exists("#objecttableview-no-items-message"))

    def test_render_single_archive_image_no_description(self):
        testrole = baker.make("cradmin_legacy_testapp.TstRole")
        archiveimage = baker.make("cradmin_imagearchive.ArchiveImage", name="Test image", description="", role=testrole)
        archiveimage.image.save("testimage.png", ContentFile(create_image(200, 100)))
        mockresponse = self.mock_http200_getrequest_htmls(
            requestuser=create_user("testuser"),
            cradmin_role=testrole,
            requestkwargs={"data": {"foreignkey_select_fieldid": "testfield"}},
        )
        self.assertEqual(
            mockresponse.selector.one(
                "#objecttableview-table tbody tr td:last-child .objecttable-cellvalue"
            ).alltext_normalized,
            "Test image",
        )
        self.assertEqual(
            mockresponse.selector.one("#objecttableview-table tbody tr td:last-child .btn-default").alltext_normalized,
            "Use this",
        )

    def test_render_single_archive_image_has_description(self):
        testrole = baker.make("cradmin_legacy_testapp.TstRole")
        archiveimage = baker.make(
            "cradmin_imagearchive.ArchiveImage", name="Test image", description="Test description", role=testrole
        )
        archiveimage.image.save("testimage.png", ContentFile(create_image(200, 100)))
        mockresponse = self.mock_http200_getrequest_htmls(
            requestuser=create_user("testuser"),
            cradmin_role=testrole,
            requestkwargs={"data": {"foreignkey_select_fieldid": "testfield"}},
        )
        self.assertEqual(
            mockresponse.selector.one(
                "#objecttableview-table tbody tr td:last-child .objecttable-cellvalue"
            ).alltext_normalized,
            "Test description",
        )
        self.assertEqual(
            mockresponse.selector.one("#objecttableview-table tbody tr td:last-child .btn-default").alltext_normalized,
            "Use this",
        )

    def test_uploadform_get_render(self):
        testrole = baker.make("cradmin_legacy_testapp.TstRole")
        mockresponse = self.mock_http200_getrequest_htmls(requestuser=create_user("testuser"), cradmin_role=testrole)
        self.assertTrue(mockresponse.selector.exists("#cradmin_legacy_imagearchive_bulkadd_form"))
        self.assertTrue(mockresponse.selector.exists("input[type=hidden][name=filecollectionid]"))
        self.assertTrue(mockresponse.selector.exists("#div_id_filecollectionid"))

    def test_uploadform_post_no_filecollectionid(self):
        self.assertEqual(ArchiveImage.objects.count(), 0)
        testrole = baker.make("cradmin_legacy_testapp.TstRole")
        mockresponse = self.mock_http200_postrequest_htmls(requestuser=create_user("testuser"), cradmin_role=testrole)
        self.assertTrue(mockresponse.selector.exists("#div_id_filecollectionid.has-error"))
        self.assertIn(
            "You must upload an image.", mockresponse.selector.one("#div_id_filecollectionid").alltext_normalized
        )

    def test_uploadform_post_single_image(self):
        testuser = create_user("testuser")
        testimage = create_image(200, 100)
        collection = TemporaryFileCollection.objects.create(user=testuser)
        temporaryfile = TemporaryFile(collection=collection, filename="testfile.png")
        temporaryfile.file.save("testfile.png", ContentFile(testimage))

        testrole = baker.make("cradmin_legacy_testapp.TstRole")
        cradmin_app = mock.MagicMock()
        self.assertEqual(ArchiveImage.objects.count(), 0)
        mockresponse = self.mock_http302_postrequest(
            requestuser=testuser,
            cradmin_role=testrole,
            cradmin_app=cradmin_app,
            requestkwargs={"data": {"filecollectionid": collection.id}},
        )

        self.assertEqual(ArchiveImage.objects.count(), 1)
        created_image = ArchiveImage.objects.first()
        self.assertTrue(
            mockresponse.response["Location"].endswith(f"?foreignkey_selected_value={created_image.pk}")
        )
        created_image.image.open()
        self.assertEqual(created_image.image.read(), testimage)
        created_image.image.close()
        self.assertEqual(created_image.name, "testfile.png")
        self.assertEqual(created_image.description, "")

    def test_uploadform_post_deletes_collection(self):
        testuser = create_user("testuser")
        testimage = create_image(200, 100)
        collection = TemporaryFileCollection.objects.create(user=testuser)
        temporaryfile = TemporaryFile(collection=collection, filename="testfile.png")
        temporaryfile.file.save("testfile.png", ContentFile(testimage))

        testrole = baker.make("cradmin_legacy_testapp.TstRole")
        self.mock_http302_postrequest(
            requestuser=testuser, cradmin_role=testrole, requestkwargs={"data": {"filecollectionid": collection.id}}
        )

        self.assertFalse(TemporaryFileCollection.objects.filter(id=collection.id).exists())

    def test_uploadform_post_multiple_images_fails(self):
        testuser = create_user("testuser")
        testimage1 = create_image(200, 100)
        testimage2 = create_image(100, 100)
        collection = TemporaryFileCollection.objects.create(user=testuser)
        temporaryfile = TemporaryFile(collection=collection, filename="testfile1.png")
        temporaryfile.file.save("testfile1.png", ContentFile(testimage1))
        temporaryfile = TemporaryFile(collection=collection, filename="testfile2.png")
        temporaryfile.file.save("testfile2.png", ContentFile(testimage2))

        testrole = baker.make("cradmin_legacy_testapp.TstRole")
        cradmin_app = mock.MagicMock()
        cradmin_app.reverse_appurl.return_value = "/success"

        self.assertEqual(ArchiveImage.objects.count(), 0)
        mockresponse = self.mock_http200_postrequest_htmls(
            requestuser=testuser,
            cradmin_role=testrole,
            cradmin_app=cradmin_app,
            requestkwargs={"data": {"filecollectionid": collection.id}},
        )
        self.assertEqual(ArchiveImage.objects.count(), 0)
        self.assertTrue(mockresponse.selector.exists("#div_id_filecollectionid.has-error"))
        self.assertIn(
            "You must upload exactly one image.",
            mockresponse.selector.one("#div_id_filecollectionid").alltext_normalized,
        )

    def test_uploadform_post_sets_file_size(self):
        testuser = create_user("testuser")
        testimage = create_image(200, 100)
        collection = TemporaryFileCollection.objects.create(user=testuser)
        temporaryfile = TemporaryFile(collection=collection, filename="testfile.png")
        temporaryfile.file.save("testfile.png", ContentFile(testimage))

        testrole = baker.make("cradmin_legacy_testapp.TstRole")
        self.mock_http302_postrequest(
            requestuser=testuser, cradmin_role=testrole, requestkwargs={"data": {"filecollectionid": collection.id}}
        )
        created_image = ArchiveImage.objects.first()
        self.assertEqual(len(testimage), created_image.file_size)
