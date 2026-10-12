import json
import os

from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TestCase

from cradmin_legacy.apps.cradmin_temporaryfileuploadstore.models import TemporaryFileCollection, TemporaryFile
from cradmin_legacy.apps.cradmin_temporaryfileuploadstore.views.temporary_file_upload_api import (
    UploadTemporaryFilesView,
)
from cradmin_legacy.tests.helpers import create_user


class TestUploadTemporaryFilesView(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.testuser = create_user("testuser")

    def test_post_single_file(self):
        request = self.factory.post("/test", {"file": SimpleUploadedFile("testfile1.txt", b"Test1")})
        request.user = self.testuser
        response = UploadTemporaryFilesView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        responsedata = json.loads(response.content.decode("utf-8"))
        self.assertIsNotNone(responsedata["collectionid"])

        collectionid = responsedata["collectionid"]
        collection = TemporaryFileCollection.objects.get(id=collectionid)
        self.assertEqual(collection.files.count(), 1)
        uploadedfile = collection.files.first()
        self.assertEqual(uploadedfile.filename, "testfile1.txt")
        self.assertNotIn("testfile1.txt", uploadedfile.file.name)
        self.assertTrue(uploadedfile.file.name.startswith(f"cradmin_temporaryfileuploadstore/{collection.id}/"))
        self.assertEqual(uploadedfile.file.read(), b"Test1")

        self.assertEqual(len(responsedata["temporaryfiles"]), 1)
        self.assertEqual(responsedata["temporaryfiles"][0]["filename"], "testfile1.txt")

    def test_post_multiple_files(self):
        request = self.factory.post(
            "/test",
            {
                "file": [
                    SimpleUploadedFile("testfile1.txt", b"Test1"),
                    SimpleUploadedFile("testfile2.txt", b"Test2"),
                ]
            },
        )
        request.user = self.testuser
        response = UploadTemporaryFilesView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        responsedata = json.loads(response.content.decode("utf-8"))
        self.assertIsNotNone(responsedata["collectionid"])

        collectionid = responsedata["collectionid"]
        collection = TemporaryFileCollection.objects.get(id=collectionid)
        self.assertEqual(collection.files.count(), 2)
        self.assertEqual(len(responsedata["temporaryfiles"]), 2)
        self.assertEqual(responsedata["temporaryfiles"][0]["filename"], "testfile1.txt")
        self.assertEqual(responsedata["temporaryfiles"][1]["filename"], "testfile2.txt")

    def test_post_multiple_requests_for_same_collection(self):
        request1 = self.factory.post("/test", {"file": SimpleUploadedFile("testfile1.txt", b"Test1")})
        request1.user = self.testuser
        response1 = UploadTemporaryFilesView.as_view()(request1)
        self.assertEqual(response1.status_code, 200)
        response1data = json.loads(response1.content.decode("utf-8"))
        self.assertIsNotNone(response1data["collectionid"])
        collectionid = response1data["collectionid"]
        collection = TemporaryFileCollection.objects.get(id=collectionid)
        self.assertEqual(collection.files.count(), 1)

        request2 = self.factory.post(
            "/test", {"file": SimpleUploadedFile("testfile2.txt", b"Test2"), "collectionid": collectionid}
        )
        request2.user = self.testuser
        response2 = UploadTemporaryFilesView.as_view()(request2)
        self.assertEqual(response2.status_code, 200)
        response2data = json.loads(response2.content.decode("utf-8"))
        self.assertEqual(collectionid, response2data["collectionid"])
        self.assertEqual(collection.files.count(), 2)

    def test_post_multiple_files_singlefile_mode(self):
        request1 = self.factory.post(
            "/test", {"file": SimpleUploadedFile("testfile1.txt", b"Test1"), "singlemode": "true"}
        )
        request1.user = self.testuser
        response1 = UploadTemporaryFilesView.as_view()(request1)
        self.assertEqual(response1.status_code, 200)
        response1data = json.loads(response1.content.decode("utf-8"))
        self.assertIsNotNone(response1data["collectionid"])
        collectionid = response1data["collectionid"]
        collection = TemporaryFileCollection.objects.get(id=collectionid)
        self.assertEqual(collection.files.count(), 1)
        uploadedfile1 = collection.files.first()
        uploadedfile1_physical_file_path = uploadedfile1.file.path
        self.assertTrue(os.path.exists(uploadedfile1_physical_file_path))

        request2 = self.factory.post(
            "/test",
            {"file": SimpleUploadedFile("testfile2.txt", b"Test2"), "collectionid": collectionid, "singlemode": "true"},
        )
        request2.user = self.testuser
        response2 = UploadTemporaryFilesView.as_view()(request2)
        self.assertEqual(response2.status_code, 200)
        response2data = json.loads(response2.content.decode("utf-8"))
        self.assertEqual(collectionid, response2data["collectionid"])
        self.assertEqual(collection.files.count(), 1)
        uploadedfile2 = collection.files.first()
        self.assertEqual(uploadedfile2.filename, "testfile2.txt")
        self.assertEqual(uploadedfile2.file.read(), b"Test2")
        self.assertFalse(os.path.exists(uploadedfile1_physical_file_path))

    def test_post_accept_ok(self):
        request = self.factory.post(
            "/test", {"file": SimpleUploadedFile("testfile1.txt", b"Test1"), "accept": "text/plain,application/pdf"}
        )
        request.user = self.testuser
        response = UploadTemporaryFilesView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        responsedata = json.loads(response.content.decode("utf-8"))
        collectionid = responsedata["collectionid"]

        collection = TemporaryFileCollection.objects.get(id=collectionid)
        self.assertEqual(collection.accept, "text/plain,application/pdf")
        self.assertEqual(collection.files.count(), 1)
        uploadedfile = collection.files.first()
        self.assertEqual(uploadedfile.mimetype, "text/plain")

        self.assertEqual(responsedata["temporaryfiles"][0]["mimetype"], "text/plain")

    def test_post_accept_invalid_single_file(self):
        request = self.factory.post(
            "/test", {"file": SimpleUploadedFile("testfile1.txt", b"Test1"), "accept": "application/pdf"}
        )
        request.user = self.testuser
        self.assertEqual(TemporaryFileCollection.objects.count(), 0)
        response = UploadTemporaryFilesView.as_view()(request)
        self.assertEqual(response.status_code, 400)
        responsedata = json.loads(response.content.decode("utf-8"))
        self.assertEqual(TemporaryFileCollection.objects.count(), 0)
        self.assertEqual(responsedata["file"][0]["code"], "unsupported_mimetype")
        self.assertEqual(responsedata["file"][0]["message"], "testfile1.txt: Unsupported filetype.")

    def test_post_accept_invalid_existing_collection(self):
        collection = TemporaryFileCollection.objects.create(user=self.testuser)
        temporaryfile = TemporaryFile(collection=collection, filename="testfile.txt")
        temporaryfile.save()

        request = self.factory.post(
            "/test",
            {
                "collectionid": collection.id,
                "file": SimpleUploadedFile("testfile1.txt", b"Test1"),
                "accept": "application/pdf",
            },
        )
        request.user = self.testuser
        self.assertEqual(TemporaryFileCollection.objects.count(), 1)
        self.assertEqual(collection.files.count(), 1)
        response = UploadTemporaryFilesView.as_view()(request)
        self.assertEqual(response.status_code, 400)
        responsedata = json.loads(response.content.decode("utf-8"))
        self.assertEqual(TemporaryFileCollection.objects.count(), 1)
        self.assertEqual(collection.files.count(), 1)
        self.assertEqual(responsedata["file"][0]["code"], "unsupported_mimetype")
        self.assertEqual(responsedata["file"][0]["message"], "testfile1.txt: Unsupported filetype.")

    def test_post_accept_invalid_multiple_files(self):
        request = self.factory.post(
            "/test",
            {
                "file": [
                    SimpleUploadedFile("testfile1.pdf", b"Test1"),
                    SimpleUploadedFile("testfile2.txt", b"Test2"),
                ],
                "accept": "application/pdf",
            },
        )
        request.user = self.testuser
        self.assertEqual(TemporaryFileCollection.objects.count(), 0)
        response = UploadTemporaryFilesView.as_view()(request)
        self.assertEqual(response.status_code, 400)
        responsedata = json.loads(response.content.decode("utf-8"))
        self.assertEqual(TemporaryFileCollection.objects.count(), 0)
        self.assertEqual(responsedata["file"][0]["code"], "unsupported_mimetype")
        self.assertEqual(responsedata["file"][0]["message"], "testfile2.txt: Unsupported filetype.")

    def test_post_max_filename_length_not_truncated(self):
        request = self.factory.post(
            "/test", {"file": SimpleUploadedFile("abc.txt", b"Testcontent"), "max_filename_length": "7"}
        )
        request.user = self.testuser
        response = UploadTemporaryFilesView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        responsedata = json.loads(response.content.decode("utf-8"))
        collectionid = responsedata["collectionid"]

        collection = TemporaryFileCollection.objects.get(id=collectionid)
        self.assertEqual(collection.files.first().filename, "abc.txt")
        self.assertEqual(responsedata["temporaryfiles"][0]["filename"], "abc.txt")

    def test_post_max_filename_length_truncated(self):
        request = self.factory.post(
            "/test", {"file": SimpleUploadedFile("abc.txt", b"Testcontent"), "max_filename_length": "6"}
        )
        request.user = self.testuser
        response = UploadTemporaryFilesView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        responsedata = json.loads(response.content.decode("utf-8"))
        collectionid = responsedata["collectionid"]

        collection = TemporaryFileCollection.objects.get(id=collectionid)
        self.assertEqual(collection.files.first().filename, "bc.txt")
        self.assertEqual(responsedata["temporaryfiles"][0]["filename"], "bc.txt")

    def test_post_unique_filenames(self):
        request = self.factory.post(
            "/test",
            {
                "file": [
                    SimpleUploadedFile("abc.txt", b"Testcontent1"),
                    SimpleUploadedFile("abc.txt", b"Testcontent2"),
                ],
                "unique_filenames": True,
            },
        )
        request.user = self.testuser
        response = UploadTemporaryFilesView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        responsedata = json.loads(response.content.decode("utf-8"))
        collectionid = responsedata["collectionid"]
        collection = TemporaryFileCollection.objects.get(id=collectionid)

        files_by_content = {}
        for temporaryfile in collection.files.all():
            files_by_content[temporaryfile.file.read()] = temporaryfile
        self.assertEqual(files_by_content[b"Testcontent1"].filename, "abc.txt")
        self.assertNotEqual(files_by_content[b"Testcontent2"].filename, "abc.txt")
        self.assertTrue(files_by_content[b"Testcontent2"].filename.endswith("abc.txt"))

        self.assertEqual(responsedata["temporaryfiles"][0]["filename"], "abc.txt")
        self.assertNotEqual(responsedata["temporaryfiles"][1]["filename"], "abc.txt")
        self.assertTrue(responsedata["temporaryfiles"][1]["filename"].endswith("abc.txt"))

    def test_post_unique_filenames_and_max_filename_length(self):
        request = self.factory.post(
            "/test",
            {
                "file": [
                    SimpleUploadedFile("t" * 50, b"Testcontent1"),
                    SimpleUploadedFile("t" * 50, b"Testcontent2"),
                ],
                "unique_filenames": True,
                "max_filename_length": 45,
            },
        )
        request.user = self.testuser
        response = UploadTemporaryFilesView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        responsedata = json.loads(response.content.decode("utf-8"))
        collectionid = responsedata["collectionid"]
        collection = TemporaryFileCollection.objects.get(id=collectionid)

        files_by_content = {}
        for temporaryfile in collection.files.all():
            files_by_content[temporaryfile.file.read()] = temporaryfile
        self.assertEqual(files_by_content[b"Testcontent1"].filename, "ttttttttttttttttttttt...ttttttttttttttttttttt")
        self.assertNotEqual(files_by_content[b"Testcontent2"].filename, "ttttttttttttttttttttt...ttttttttttttttttttttt")
        self.assertTrue(files_by_content[b"Testcontent2"].filename.endswith("-tttttttt"))

    def test_post_max_filesize_bytes_size_below_ok(self):
        request = self.factory.post(
            "/test", {"file": SimpleUploadedFile("testname.txt", b"Testcontent"), "max_filesize_bytes": 100}
        )
        request.user = self.testuser
        response = UploadTemporaryFilesView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        responsedata = json.loads(response.content.decode("utf-8"))
        collectionid = responsedata["collectionid"]
        collection = TemporaryFileCollection.objects.get(id=collectionid)
        self.assertEqual(collection.files.count(), 1)

    def test_post_max_filesize_bytes_size_above_fails(self):
        request = self.factory.post(
            "/test", {"file": SimpleUploadedFile("testname.txt", b"Testcontent"), "max_filesize_bytes": 1}
        )
        request.user = self.testuser
        response = UploadTemporaryFilesView.as_view()(request)
        self.assertEqual(response.status_code, 400)
        responsedata = json.loads(response.content.decode("utf-8"))
        self.assertEqual("max_filesize_bytes_exceeded", responsedata["file"][0]["code"])
        self.assertFalse(TemporaryFileCollection.objects.exists())

    def test_post_form_invalid_no_file(self):
        request = self.factory.post("/test")
        request.user = self.testuser
        response = UploadTemporaryFilesView.as_view()(request)
        self.assertEqual(response.status_code, 400)
        responsedata = json.loads(response.content.decode("utf-8"))
        self.assertEqual(responsedata["file"][0]["code"], "required")
        self.assertFalse(TemporaryFileCollection.objects.exists())

    def test_post_form_invalid_collectionid_not_number(self):
        request = self.factory.post(
            "/test", {"file": SimpleUploadedFile("testfile1.txt", b"Test1"), "collectionid": "invalid"}
        )
        request.user = self.testuser
        response = UploadTemporaryFilesView.as_view()(request)
        self.assertEqual(response.status_code, 400)
        responsedata = json.loads(response.content.decode("utf-8"))
        self.assertEqual(responsedata["collectionid"][0]["code"], "invalid")

    def test_post_form_collectionid_does_not_exist(self):
        request = self.factory.post(
            "/test", {"file": SimpleUploadedFile("testfile1.txt", b"Test1"), "collectionid": "10001"}
        )
        request.user = self.testuser
        response = UploadTemporaryFilesView.as_view()(request)
        self.assertEqual(response.status_code, 404)
        responsedata = json.loads(response.content.decode("utf-8"))
        self.assertEqual(responsedata["collectionid"][0]["code"], "doesnotexist")

    def test_post_form_collection_not_owned_by_user(self):
        collection = TemporaryFileCollection.objects.create(user=self.testuser)
        request = self.factory.post(
            "/test", {"file": SimpleUploadedFile("testfile1.txt", b"Test1"), "collectionid": collection.id}
        )
        request.user = create_user("otheruser")
        response = UploadTemporaryFilesView.as_view()(request)
        self.assertEqual(response.status_code, 404)
        responsedata = json.loads(response.content.decode("utf-8"))
        self.assertEqual(responsedata["collectionid"][0]["code"], "doesnotexist")

    def test_delete_single_file(self):
        collection = TemporaryFileCollection.objects.create(user=self.testuser)
        temporaryfile = TemporaryFile(collection=collection, filename="testfile.txt")
        temporaryfile.file.save("testfile.txt", ContentFile("testcontent"))

        request = self.factory.delete(
            "/test", json.dumps({"collectionid": collection.id, "temporaryfileid": temporaryfile.id})
        )
        request.user = self.testuser
        response = UploadTemporaryFilesView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        responsedata = json.loads(response.content.decode("utf-8"))

        self.assertEqual(responsedata["collectionid"], collection.id)
        self.assertEqual(responsedata["temporaryfileid"], temporaryfile.id)

        self.assertTrue(TemporaryFileCollection.objects.filter(id=collection.id).exists())
        self.assertFalse(TemporaryFile.objects.filter(id=temporaryfile.id).exists())

    def test_delete_invalid_json_reqeust(self):
        request = self.factory.delete("/test", data="invalid")
        request.user = self.testuser
        response = UploadTemporaryFilesView.as_view()(request)
        self.assertEqual(response.status_code, 400)
        responsedata = json.loads(response.content.decode("utf-8"))
        self.assertEqual(responsedata["errormessage"], "Invalid JSON data in the request body.")

    def test_delete_form_collectionid_does_not_exist(self):
        request = self.factory.delete(
            "/test",
            data=json.dumps(
                {
                    "collectionid": "10001",
                    "temporaryfileid": "1",  # NOTE: This is ignored since we never get to the code looking it up
                }
            ),
        )
        request.user = self.testuser
        response = UploadTemporaryFilesView.as_view()(request)
        self.assertEqual(response.status_code, 404)
        responsedata = json.loads(response.content.decode("utf-8"))
        self.assertEqual(responsedata["collectionid"][0]["code"], "doesnotexist")

    def test_delete_form_collection_not_owned_by_user(self):
        collection = TemporaryFileCollection.objects.create(user=self.testuser)
        request = self.factory.delete(
            "/test",
            json.dumps(
                {
                    "collectionid": collection.id,
                    "temporaryfileid": "1",  # NOTE: This is ignored since we never get to the code looking it up
                }
            ),
        )
        request.user = create_user("otheruser")
        response = UploadTemporaryFilesView.as_view()(request)
        self.assertEqual(response.status_code, 404)
        responsedata = json.loads(response.content.decode("utf-8"))
        self.assertEqual(responsedata["collectionid"][0]["code"], "doesnotexist")

    def test_delete_form_temporaryfileid_does_not_exist(self):
        collection = TemporaryFileCollection.objects.create(user=self.testuser)
        request = self.factory.delete(
            "/test", data=json.dumps({"collectionid": collection.id, "temporaryfileid": 10001})
        )
        request.user = self.testuser
        response = UploadTemporaryFilesView.as_view()(request)
        self.assertEqual(response.status_code, 404)
        responsedata = json.loads(response.content.decode("utf-8"))
        self.assertEqual(responsedata["temporaryfileid"][0]["code"], "doesnotexist")
