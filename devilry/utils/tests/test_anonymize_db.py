from django import test
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.test import override_settings
from model_mommy import mommy

from devilry.devilry_account.models import UserEmail, UserName
from devilry.devilry_comment.models import Comment, CommentEditHistory, CommentFile
from devilry.devilry_group.models import GroupComment, GroupCommentEditHistory
from devilry.utils import anonymize_database


class AnonymizeDbTestMixin:
    def create_useremail(self, user, email):
        return mommy.make('devilry_account.UserEmail', email=email, user=user)

    def create_username(self, user, username):
        return mommy.make('devilry_account.UserName', username=username, user=user)


class TestAnonymizeString(test.TestCase):
    def test_simple_lowercase_string(self):
        string_to_anonymize = 'test'
        anonymized_string = anonymize_database.AnonymizeDatabase().randomize_string(
            unanonymized_string=string_to_anonymize)
        self.assertNotEqual(anonymized_string, string_to_anonymize)
        self.assertEqual(len(anonymized_string), len(string_to_anonymize))
        self.assertTrue(anonymized_string.islower())

    def test_simple_uppercase_string(self):
        string_to_anonymize = 'TEST'
        anonymized_string = anonymize_database.AnonymizeDatabase().randomize_string(
            unanonymized_string=string_to_anonymize)
        self.assertNotEqual(anonymized_string, string_to_anonymize)
        self.assertEqual(len(anonymized_string), len(string_to_anonymize))
        self.assertTrue(anonymized_string.isupper())

    def test_upper_and_lowercase(self):
        string_to_anonymize = 'TeSt'
        anonymized_string = anonymize_database.AnonymizeDatabase().randomize_string(
            unanonymized_string=string_to_anonymize)
        self.assertNotEqual(anonymized_string, string_to_anonymize)
        self.assertEqual(len(anonymized_string), len(string_to_anonymize))
        self.assertTrue(anonymized_string[0].isupper())
        self.assertTrue(anonymized_string[1].islower())
        self.assertTrue(anonymized_string[2].isupper())
        self.assertTrue(anonymized_string[3].islower())

    def test_upper_and_lowercase_with_digits(self):
        string_to_anonymize = 'Te2St6'
        anonymized_string = anonymize_database.AnonymizeDatabase().randomize_string(
            unanonymized_string=string_to_anonymize)
        self.assertNotEqual(anonymized_string, string_to_anonymize)
        self.assertEqual(len(anonymized_string), len(string_to_anonymize))
        self.assertTrue(anonymized_string[0].isupper())
        self.assertTrue(anonymized_string[1].islower())
        self.assertTrue(anonymized_string[2].isdigit())
        self.assertTrue(anonymized_string[3].isupper())
        self.assertTrue(anonymized_string[4].islower())
        self.assertTrue(anonymized_string[5].isdigit())

    def test_whitespace_character(self):
        string_to_anonymize = 'Test Test'
        anonymized_string = anonymize_database.AnonymizeDatabase().randomize_string(
            unanonymized_string=string_to_anonymize)
        self.assertNotEqual(anonymized_string, string_to_anonymize)
        self.assertEqual(len(anonymized_string), len(string_to_anonymize))
        self.assertEqual(anonymized_string[4], ' ')


class TestAnonymizeUserFast(AnonymizeDbTestMixin, test.TestCase):
    def test_anonymize_user_shortname(self):
        user = mommy.make(settings.AUTH_USER_MODEL, shortname='testuser')
        anonymize_database.AnonymizeDatabase().anonymize_user()
        self.assertEqual(
            get_user_model().objects.get(id=user.id).shortname,
            '{}'.format(user.id))

    @override_settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=True)
    def test_shortname_is_anonymized_with_email_if_django_cradmin_user_email_auth_backend_is_true(self):
        user = mommy.make(settings.AUTH_USER_MODEL, shortname='testuser')
        anonymize_database.AnonymizeDatabase().anonymize_user()
        self.assertEqual(
            get_user_model().objects.get(id=user.id).shortname,
            '{}@example.com'.format(user.id))

    def test_anonymize_user_email(self):
        user = mommy.make(settings.AUTH_USER_MODEL, shortname='testuser')
        useremail = self.create_useremail(email='testuser@example.com', user=user)
        anonymize_database.AnonymizeDatabase().anonymize_user()
        self.assertEqual(UserEmail.objects.get(id=useremail.id).email,
                         '{}_{}@example.com'.format(user.id, useremail.id))

    def test_anonymize_user_name(self):
        user = mommy.make(settings.AUTH_USER_MODEL, shortname='testuser')
        username = self.create_username(username='testuser', user=user)
        anonymize_database.AnonymizeDatabase().anonymize_user()
        self.assertEqual(
            UserName.objects.get(id=username.id).username,
            '{}_{}'.format(user.id, username.id))

    def test_anonymize_multiple_users(self):
        user1 = mommy.make(settings.AUTH_USER_MODEL, shortname='testuser1')
        user2 = mommy.make(settings.AUTH_USER_MODEL, shortname='testuser2')
        user3 = mommy.make(settings.AUTH_USER_MODEL, shortname='testuser3')
        anonymize_database.AnonymizeDatabase().anonymize_user()
        self.assertEqual(get_user_model().objects.get(id=user1.id).shortname, str(user1.id))
        self.assertEqual(get_user_model().objects.get(id=user2.id).shortname, str(user2.id))
        self.assertEqual(get_user_model().objects.get(id=user3.id).shortname, str(user3.id))

    def test_anonymize_multiple_useremails_for_same_user(self):
        user = mommy.make(settings.AUTH_USER_MODEL, shortname='testuser1@example.com')
        useremail1 = self.create_useremail(email='testuser1@example.com', user=user)
        useremail2 = self.create_useremail(email='testuser2@example.com', user=user)
        anonymize_database.AnonymizeDatabase().anonymize_user()
        self.assertTrue(UserEmail.objects.filter(email='{}_{}@example.com'.format(
            user.id, useremail1.id)))
        self.assertTrue(UserEmail.objects.filter(email='{}_{}@example.com'.format(
            user.id, useremail2.id)))

    def test_anonymize_multiple_user_emails(self):
        user1 = mommy.make(settings.AUTH_USER_MODEL, shortname='testuser1@example.com')
        user2 = mommy.make(settings.AUTH_USER_MODEL, shortname='testuser2@example.com')
        user3 = mommy.make(settings.AUTH_USER_MODEL, shortname='testuser3@example.com')
        useremail1 = self.create_useremail(email='testuser1@example.com', user=user1)
        useremail2 = self.create_useremail(email='testuser2@example.com', user=user2)
        useremail3 = self.create_useremail(email='testuser3@example.com', user=user3)
        anonymize_database.AnonymizeDatabase().anonymize_user()
        self.assertEqual(
            UserEmail.objects.get(id=useremail1.id).email,
            '{}_{}@example.com'.format(user1.id, useremail1.id))
        self.assertEqual(
            UserEmail.objects.get(id=useremail2.id).email,
            '{}_{}@example.com'.format(user2.id, useremail2.id))
        self.assertEqual(
            UserEmail.objects.get(id=useremail3.id).email,
            '{}_{}@example.com'.format(user3.id, useremail3.id))

    def test_anonymize_multiple_usernames_for_same_user(self):
        user = mommy.make(settings.AUTH_USER_MODEL, shortname='testuser1')
        username1 = self.create_username(username='testuser1', user=user)
        username2 = self.create_username(username='testuser2', user=user)
        anonymize_database.AnonymizeDatabase().anonymize_user()
        self.assertEqual(
            UserName.objects.get(id=username1.id).username,
            '{}_{}'.format(user.id, username1.id))
        self.assertEqual(
            UserName.objects.get(id=username2.id).username,
            '{}_{}'.format(user.id, username2.id))

    def test_anonymize_multiple_user_names(self):
        user1 = mommy.make(settings.AUTH_USER_MODEL, shortname='testuser1')
        user2 = mommy.make(settings.AUTH_USER_MODEL, shortname='testuser2')
        user3 = mommy.make(settings.AUTH_USER_MODEL, shortname='testuser3')
        username1 = self.create_username(username='testuser1', user=user1)
        username2 = self.create_username(username='testuser2', user=user2)
        username3 = self.create_username(username='testuser3', user=user3)
        anonymize_database.AnonymizeDatabase().anonymize_user()
        self.assertEqual(
            UserName.objects.get(id=username1.id).username,
            '{}_{}'.format(user1.id, username1.id))
        self.assertEqual(
            UserName.objects.get(id=username2.id).username,
            '{}_{}'.format(user2.id, username2.id))
        self.assertEqual(
            UserName.objects.get(id=username3.id).username,
            '{}_{}'.format(user3.id, username3.id))


class TestAnonymizeUser(AnonymizeDbTestMixin, test.TestCase):
    def test_anonymize_user_shortname(self):
        shortname_to_anonymize = 'testuser'
        mommy.make(settings.AUTH_USER_MODEL, shortname=shortname_to_anonymize)
        anonymize_database.AnonymizeDatabase(fast=False).anonymize_user()

        self.assertFalse(get_user_model().objects.filter(shortname=shortname_to_anonymize).exists())
        anonymized_user = get_user_model().objects.get()
        self.assertEqual(len(anonymized_user.shortname), len(shortname_to_anonymize))
        self.assertNotEqual(anonymized_user.shortname, shortname_to_anonymize)

    def test_anonymize_user_fullname(self):
        fullname_to_anonymize = 'Test User'
        mommy.make(settings.AUTH_USER_MODEL, fullname=fullname_to_anonymize)
        anonymize_database.AnonymizeDatabase(fast=False).anonymize_user()

        self.assertFalse(get_user_model().objects.filter(fullname=fullname_to_anonymize).exists())
        anonymized_user = get_user_model().objects.get()
        self.assertEqual(len(anonymized_user.fullname), len(fullname_to_anonymize))
        self.assertNotEqual(anonymized_user.fullname, fullname_to_anonymize)

    def test_anonymize_user_lastname(self):
        lastname_to_anonymize = 'Userlastname'
        mommy.make(settings.AUTH_USER_MODEL, lastname=lastname_to_anonymize)
        anonymize_database.AnonymizeDatabase(fast=False).anonymize_user()

        self.assertFalse(get_user_model().objects.filter(lastname=lastname_to_anonymize).exists())
        anonymized_user = get_user_model().objects.get()
        self.assertEqual(len(anonymized_user.lastname), len(lastname_to_anonymize))
        self.assertNotEqual(anonymized_user.lastname, lastname_to_anonymize)

    def test_anonymize_useremail(self):
        useremail_to_anonymize = 'testuser@test.com'
        user = mommy.make(settings.AUTH_USER_MODEL)
        self.create_useremail(email=useremail_to_anonymize, user=user)
        anonymize_database.AnonymizeDatabase(fast=False).anonymize_user()

        self.assertFalse(UserEmail.objects.filter(email=useremail_to_anonymize).exists())
        anonymized_useremail = UserEmail.objects.get().email
        self.assertEqual(len(anonymized_useremail.split('@')[0]), len('testuser'))
        self.assertNotEqual(anonymized_useremail.split('@')[0], useremail_to_anonymize)
        self.assertEqual(anonymized_useremail.split('@')[1], 'example.com')

    def test_anonymize_username(self):
        username_to_anonymize = 'testuser'
        user = mommy.make(settings.AUTH_USER_MODEL)
        self.create_username(username=username_to_anonymize, user=user)
        anonymize_database.AnonymizeDatabase(fast=False).anonymize_user()

        self.assertFalse(UserName.objects.filter(username=username_to_anonymize).exists())
        anonymized_username = UserName.objects.get().username
        self.assertNotEqual(username_to_anonymize, anonymized_username)
        self.assertEqual(len(anonymized_username), len(username_to_anonymize))


class TestAnonymizeCommentFast(test.TestCase):
    def test_anonymize_comment_text(self):
        comment_text = 'This is a comment.'
        testcomment = mommy.make('devilry_comment.Comment', text=comment_text)
        self.assertEqual(testcomment.text, 'This is a comment.')
        anonymize_database.AnonymizeDatabase().anonymize_comments()
        self.assertFalse(Comment.objects.filter(text=comment_text).exists())
        self.assertEqual(Comment.objects.get().text, anonymize_database.lorem_ipsum)

    def test_anonymize_comment_edit_history(self):
        testedithistory = mommy.make('devilry_comment.CommentEditHistory', post_edit_text='Test', pre_edit_text='Tst')
        self.assertEqual(testedithistory.post_edit_text, 'Test')
        self.assertEqual(testedithistory.pre_edit_text, 'Tst')
        anonymize_database.AnonymizeDatabase().anonymize_comments()
        self.assertFalse(CommentEditHistory.objects.filter(post_edit_text='Test', pre_edit_text='Tst').exists())
        self.assertEqual(CommentEditHistory.objects.get().post_edit_text, anonymize_database.lorem_ipsum)
        self.assertEqual(CommentEditHistory.objects.get().pre_edit_text, anonymize_database.lorem_ipsum)

    def test_anonymize_comment_file_name(self):
        testcommentfile = mommy.make('devilry_comment.CommentFile', filename='Test.txt')
        self.assertEqual(testcommentfile.filename, 'Test.txt')
        anonymize_database.AnonymizeDatabase().anonymize_comments()
        self.assertFalse(CommentFile.objects.filter(filename='Test.txt').exists())
        self.assertEqual(CommentFile.objects.get().filename, str(testcommentfile.id))

    def test_anonymize_group_comment_text(self):
        comment_text = 'This is a comment.'
        testcomment = mommy.make('devilry_group.GroupComment', text=comment_text)
        self.assertEqual(testcomment.text, 'This is a comment.')
        anonymize_database.AnonymizeDatabase().anonymize_comments()
        self.assertFalse(Comment.objects.filter(text=comment_text).exists())
        self.assertFalse(GroupComment.objects.filter(text=comment_text).exists())
        self.assertEqual(GroupComment.objects.get().text, anonymize_database.lorem_ipsum)

    def test_anonymize_group_comment_edit_history(self):
        testedithistory = mommy.make('devilry_group.GroupCommentEditHistory', post_edit_text='Test', pre_edit_text='Tst')
        self.assertEqual(testedithistory.post_edit_text, 'Test')
        self.assertEqual(testedithistory.pre_edit_text, 'Tst')
        anonymize_database.AnonymizeDatabase().anonymize_comments()
        self.assertFalse(CommentEditHistory.objects.filter(post_edit_text='Test', pre_edit_text='Tst').exists())
        self.assertFalse(GroupCommentEditHistory.objects.filter(post_edit_text='Test', pre_edit_text='Tst').exists())
        self.assertEqual(GroupCommentEditHistory.objects.get().post_edit_text, anonymize_database.lorem_ipsum)
        self.assertEqual(GroupCommentEditHistory.objects.get().pre_edit_text, anonymize_database.lorem_ipsum)
