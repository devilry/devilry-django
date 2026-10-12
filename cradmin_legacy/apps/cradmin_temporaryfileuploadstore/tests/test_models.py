import os
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.test import TestCase
from model_bakery import baker
from cradmin_legacy.apps.cradmin_temporaryfileuploadstore.models import (
    TemporaryFileCollection,
    TemporaryFile,
    html_input_accept_match,
    truncate_filename,
    make_unique_filename,
)
from cradmin_legacy.tests.helpers import create_user


class TestModels(TestCase):
    def test_delete_removes_physical_file(self):
        collection = TemporaryFileCollection.objects.create(user=create_user("testuser"))
        temporaryfile = TemporaryFile(filename="test.txt", collection=collection)
        temporaryfile.file.save("test.txt", ContentFile("Testdata"))
        physical_file_path = temporaryfile.file.path
        self.assertTrue(os.path.exists(physical_file_path))
        temporaryfile.file.delete()
        temporaryfile.delete()
        self.assertFalse(os.path.exists(physical_file_path))

    def test_clear_collection(self):
        collection = TemporaryFileCollection.objects.create(user=create_user("testuser"))
        temporaryfile = TemporaryFile(filename="test.txt", collection=collection)
        temporaryfile.file.save("test.txt", ContentFile("Testdata"))
        physical_file_path = temporaryfile.file.path
        self.assertTrue(os.path.exists(physical_file_path))
        collection.clear_files()
        self.assertFalse(os.path.exists(physical_file_path))
        self.assertEqual(collection.files.count(), 0)

    def test_singlemode_keeps_only_last_file(self):
        collection = TemporaryFileCollection.objects.create(user=create_user("testuser"), singlemode=True)

        first_added_temporary_file = TemporaryFile(filename="test1.txt", collection=collection)
        first_added_temporary_file.file.save("test1.txt", ContentFile("Testdata"), save=False)
        first_added_temporary_file.clean()
        first_added_temporary_file.save()

        last_added_temporary_file = TemporaryFile(filename="test2.txt", collection=collection)
        last_added_temporary_file.file.save("test1.txt", ContentFile("Testdata"), save=False)
        last_added_temporary_file.clean()
        last_added_temporary_file.save()
        self.assertEqual(collection.files.count(), 1)
        self.assertEqual(collection.files.first(), last_added_temporary_file)

    def test_singlemode_keeps_only_last_file_delete_physical_file(self):
        collection = TemporaryFileCollection.objects.create(user=create_user("testuser"), singlemode=True)

        first_added_temporary_file = TemporaryFile(filename="test1.txt", collection=collection)
        first_added_temporary_file.file.save("test1.txt", ContentFile("Testdata"), save=False)
        first_added_temporary_file.clean()
        first_added_temporary_file.save()
        first_added_physical_file_path = first_added_temporary_file.file.path
        self.assertTrue(os.path.exists(first_added_physical_file_path))

        last_added_temporary_file = TemporaryFile(filename="test2.txt", collection=collection)
        last_added_temporary_file.file.save("test1.txt", ContentFile("Testdata"), save=False)
        last_added_temporary_file.clean()
        self.assertFalse(os.path.exists(first_added_physical_file_path))

    def test_singlemode_keeps_only_last_file_do_not_delete_last(self):
        collection = TemporaryFileCollection.objects.create(user=create_user("testuser"), singlemode=True)

        last_added_temporary_file = TemporaryFile(filename="test2.txt", collection=collection)
        last_added_temporary_file.file.save("test1.txt", ContentFile("Testdata"), save=False)
        last_added_temporary_file.clean()
        last_added_temporary_file.save()
        last_added_temporary_file.clean()
        self.assertEqual(collection.files.count(), 1)
        self.assertEqual(collection.files.first(), last_added_temporary_file)

    def test_get_filename_set(self):
        collection = TemporaryFileCollection.objects.create(user=create_user("testuser"))
        temporaryfile1 = TemporaryFile(filename="test.txt", collection=collection)
        temporaryfile1.file.save("x", ContentFile("Testdata"))
        temporaryfile2 = TemporaryFile(filename="test2.txt", collection=collection)
        temporaryfile2.file.save("y", ContentFile("Testdata"))
        temporaryfile3 = TemporaryFile(filename="test.txt", collection=collection)
        temporaryfile3.file.save("z", ContentFile("Testdata"))
        self.assertEqual(collection.get_filename_set(), {"test.txt", "test2.txt"})

    def test_set_mimetype_from_filename(self):
        temporaryfile = TemporaryFile(filename="test.png")
        temporaryfile.set_mimetype_from_filename()
        self.assertEqual(temporaryfile.mimetype, "image/png")

    def test_set_mimetype_from_filename_no_extension(self):
        temporaryfile = TemporaryFile(filename="test")
        temporaryfile.set_mimetype_from_filename()
        self.assertEqual(temporaryfile.mimetype, "")

    def test_set_mimetype_from_filename_unknown_extension(self):
        temporaryfile = TemporaryFile(filename="test.thisdoesnotexist")
        temporaryfile.set_mimetype_from_filename()
        self.assertEqual(temporaryfile.mimetype, "")

    def clean_sets_mimetype(self):
        temporaryfile = TemporaryFile(filename="test.png")
        temporaryfile.clean()
        self.assertEqual(temporaryfile.mimetype, "image/png")

    def clean_truncates_filename(self):
        collection = TemporaryFileCollection(max_filename_length=6)
        temporaryfile = TemporaryFile(filename="test.png", collection=collection)
        temporaryfile.clean()
        self.assertEqual(temporaryfile.filename, "st.png")

    def clean_does_not_truncate_filename_if_max_filename_length_is_none(self):
        collection = TemporaryFileCollection(max_filename_length=None)
        temporaryfile = TemporaryFile(filename="test.png", collection=collection)
        temporaryfile.clean()
        self.assertEqual(temporaryfile.filename, "test.png")

    def clean_validates_accept(self):
        collection = TemporaryFileCollection.objects.create(user=create_user("testuser"), accept="image/png,image/jpeg")
        TemporaryFile(filename="test.png", collection=collection).clean()
        TemporaryFile(filename="test.jpg", collection=collection).clean()
        with self.assertRaises(ValidationError):
            TemporaryFile(filename="test.txt", collection=collection).clean()

    def test_html_input_accept_match_filename_star(self):
        self.assertTrue(html_input_accept_match(accept="*.jpg", mimetype="unused", filename="test.jpg"))
        self.assertFalse(html_input_accept_match(accept="*.jpg", mimetype="unused", filename="test.jpeg"))
        self.assertTrue(html_input_accept_match(accept=".unused,*.jpg,.unused", mimetype="unused", filename="test.jpg"))

    def test_html_input_accept_match_filename_dot(self):
        self.assertTrue(html_input_accept_match(accept=".jpg", mimetype="unused", filename="test.jpg"))
        self.assertFalse(html_input_accept_match(accept=".jpg", mimetype="unused", filename="test.jpeg"))
        self.assertTrue(html_input_accept_match(accept=".unused,.jpg,.unused", mimetype="unused", filename="test.jpg"))

    def test_html_input_accept_match_mimetype_exact(self):
        self.assertTrue(html_input_accept_match(accept="image/jpeg", mimetype="image/jpeg", filename="unused"))
        self.assertFalse(html_input_accept_match(accept="image/png", mimetype="image/jpeg", filename="unused"))
        self.assertTrue(
            html_input_accept_match(accept=".unused,image/jpeg,unused2", mimetype="image/jpeg", filename="unused")
        )

    def test_html_input_accept_match_mimetype_star(self):
        self.assertTrue(html_input_accept_match(accept="image/*", mimetype="image/jpeg", filename="unused"))
        self.assertFalse(html_input_accept_match(accept="application/*", mimetype="image/jpeg", filename="unused"))
        self.assertTrue(
            html_input_accept_match(accept=".unused,image/*,.unused2", mimetype="image/jpeg", filename="unused")
        )

    def test_html_input_accept_match_mimetype_none(self):
        self.assertFalse(html_input_accept_match(accept="image/jpeg", mimetype=None, filename="test.jpeg"))

    def test_truncate_filename_not_above_max_length(self):
        self.assertEqual(truncate_filename("test.txt", maxlength=8), "test.txt")

    def test_truncate_filename_veryshort_maxlength(self):
        self.assertEqual(truncate_filename("test.txt", maxlength=5), "t.txt")

    def test_truncate_filename_ellipsis_even_filelength_more_in_tail(self):
        self.assertEqual(truncate_filename("abcdefghABCDEFGH", maxlength=14), "abcde...CDEFGH")

    def test_truncate_filename_ellipsis_odd_filelength(self):
        self.assertEqual(truncate_filename("abcdeX___Xhijkl", maxlength=13), "abcde...hijkl")

    def test_make_unique_filename_already_unique(self):
        self.assertEqual(make_unique_filename(filename_set={"test.txt"}, wanted_filename="test2.txt"), "test2.txt")

    def test_make_unique_filename(self):
        self.assertNotEqual(make_unique_filename(filename_set={"test.txt"}, wanted_filename="test.txt"), "test.txt")
        self.assertTrue(
            make_unique_filename(filename_set={"test.txt"}, wanted_filename="test.txt").endswith("-test.txt")
        )

    def test_make_unique_filename_maxlength(self):
        unique_filename = make_unique_filename(
            filename_set={"t" * 45}, wanted_filename="t" * 45, max_filename_length=45
        )
        self.assertNotEqual(unique_filename, "t" * 45)
        self.assertTrue(unique_filename.endswith("-tttttttt"))
        self.assertEqual(len(unique_filename), 45)

    def test_no_max_filesize_bytes(self):
        collection = baker.make("cradmin_temporaryfileuploadstore.TemporaryFileCollection")
        temporaryfile = TemporaryFile(filename="test.txt", collection=collection)
        temporaryfile.file.save("test.txt", ContentFile("Testdata"))
        temporaryfile.clean()  # No ValidationError

    def test_max_filesize_bytes_size_below_ok(self):
        collection = baker.make("cradmin_temporaryfileuploadstore.TemporaryFileCollection", max_filesize_bytes=100)
        temporaryfile = TemporaryFile(filename="test.txt", collection=collection)
        temporaryfile.file.save("test.txt", ContentFile("Testdata"))
        temporaryfile.clean()  # No ValidationError

    def test_max_filesize_bytes_size_above_fails(self):
        collection = baker.make("cradmin_temporaryfileuploadstore.TemporaryFileCollection", max_filesize_bytes=1)
        temporaryfile = TemporaryFile(filename="test.txt", collection=collection)
        temporaryfile.file.save("test.txt", ContentFile("Testdata"))
        with self.assertRaisesMessage(ValidationError, "Can not upload files larger than 1B."):
            temporaryfile.clean()
