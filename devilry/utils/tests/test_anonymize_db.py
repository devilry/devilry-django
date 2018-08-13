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
    def create_user(self, **user_kwargs):
        anonymize_db_user = mommy.prepare(settings.AUTH_USER_MODEL, **user_kwargs)
        anonymize_db_user.save(using=self.anonymize_db_alias)
        default_db_user = mommy.make(settings.AUTH_USER_MODEL, **user_kwargs)
        return anonymize_db_user, default_db_user

    def create_useremail(self, default_db_user, anon_db_user, email):
        anonymize_db_useremail = mommy.prepare('devilry_account.UserEmail', email=email, user=anon_db_user)
        anonymize_db_useremail.save(using=self.anonymize_db_alias)
        default_db_useremail = mommy.make('devilry_account.UserEmail', email=email, user=default_db_user)
        return anonymize_db_useremail, default_db_useremail

    def create_username(self, default_db_user, anon_db_user, username):
        anonymize_db_username = mommy.prepare('devilry_account.UserName', username=username, user=anon_db_user)
        anonymize_db_username.save(using=self.anonymize_db_alias)
        default_db_useremail = mommy.make('devilry_account.UserName', username=username, user=default_db_user)
        return anonymize_db_username, default_db_useremail


class TestAnonymizeString(test.TestCase):
    def test_simple_lowercase_string(self):
        string_to_anonymize = 'test'
        anonymized_string = anonymize_database.AnonymizeDatabase(db_alias='test').randomize_string(
            unanonymized_string=string_to_anonymize)
        self.assertNotEqual(anonymized_string, string_to_anonymize)
        self.assertEqual(len(anonymized_string), len(string_to_anonymize))
        self.assertTrue(anonymized_string.islower())

    def test_simple_uppercase_string(self):
        string_to_anonymize = 'TEST'
        anonymized_string = anonymize_database.AnonymizeDatabase(db_alias='test').randomize_string(
            unanonymized_string=string_to_anonymize)
        self.assertNotEqual(anonymized_string, string_to_anonymize)
        self.assertEqual(len(anonymized_string), len(string_to_anonymize))
        self.assertTrue(anonymized_string.isupper())

    def test_upper_and_lowercase(self):
        string_to_anonymize = 'TeSt'
        anonymized_string = anonymize_database.AnonymizeDatabase(db_alias='test').randomize_string(
            unanonymized_string=string_to_anonymize)
        self.assertNotEqual(anonymized_string, string_to_anonymize)
        self.assertEqual(len(anonymized_string), len(string_to_anonymize))
        self.assertTrue(anonymized_string[0].isupper())
        self.assertTrue(anonymized_string[1].islower())
        self.assertTrue(anonymized_string[2].isupper())
        self.assertTrue(anonymized_string[3].islower())

    def test_upper_and_lowercase_with_digits(self):
        string_to_anonymize = 'Te2St6'
        anonymized_string = anonymize_database.AnonymizeDatabase(db_alias='test').randomize_string(
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
        anonymized_string = anonymize_database.AnonymizeDatabase(db_alias='test').randomize_string(
            unanonymized_string=string_to_anonymize)
        self.assertNotEqual(anonymized_string, string_to_anonymize)
        self.assertEqual(len(anonymized_string), len(string_to_anonymize))
        self.assertEqual(anonymized_string[4], ' ')


class TestAnonymizeUserFast(AnonymizeDbTestMixin, test.TestCase):
    anonymize_db_alias = 'anonymize_db'
    multi_db = True

    def test_passing_default_db_raises_exception(self):
        with self.assertRaises(anonymize_database.AnonymizeDatabaseException):
            anonymize_database.AnonymizeDatabase(db_alias='default')

    def test_user_in_default_db_not_changed(self):
        a_user, d_user = self.create_user(shortname='testuser')
        anonymize_database.AnonymizeDatabase(db_alias=self.anonymize_db_alias).anonymize_user()
        self.assertNotEqual(get_user_model().objects.using(self.anonymize_db_alias).get(id=d_user.id).shortname,
                            'testuser')
        self.assertEqual(get_user_model().objects.get(id=d_user.id).shortname, 'testuser')

    def test_useremail_in_default_db_not_changed(self):
        a_user, d_user = self.create_user()
        a_useremail, d_useremail = self.create_useremail(
            email='testuser@example.com',
            anon_db_user=a_user,
            default_db_user=d_user)
        anonymize_database.AnonymizeDatabase(db_alias=self.anonymize_db_alias).anonymize_user()
        self.assertNotEqual(UserEmail.objects.using(self.anonymize_db_alias).get(id=d_useremail.id).email,
                         'testuser@example.com')
        self.assertEqual(UserEmail.objects.get(id=d_useremail.id).email, 'testuser@example.com')

    def test_username_in_default_db_not_changed(self):
        a_user, d_user = self.create_user(shortname='testuser')
        a_username, d_username = self.create_username(
            default_db_user=d_user, anon_db_user=a_user, username='testuser')
        anonymize_database.AnonymizeDatabase(db_alias=self.anonymize_db_alias).anonymize_user()
        self.assertNotEqual(UserName.objects.using(self.anonymize_db_alias).get(id=d_username.id).username, 'testuser')
        self.assertEqual(UserName.objects.get(id=d_username.id).username, 'testuser')

    def test_all_user_models_in_default_db_not_changed(self):
        a_user, d_user = self.create_user(shortname='testuser')
        self.create_useremail(
            email='testuser@example.com',
            anon_db_user=a_user,
            default_db_user=d_user)
        self.create_username(
            default_db_user=d_user, anon_db_user=a_user, username='testuser')
        anonymize_database.AnonymizeDatabase(db_alias=self.anonymize_db_alias).anonymize_user()
        self.assertEqual(get_user_model().objects.get().shortname, 'testuser')
        self.assertEqual(UserEmail.objects.get().email, 'testuser@example.com')
        self.assertEqual(UserName.objects.get().username, 'testuser')

    def test_anonymize_user_shortname(self):
        a_user, d_user = self.create_user(shortname='testuser')
        anonymize_database.AnonymizeDatabase(db_alias=self.anonymize_db_alias).anonymize_user()
        self.assertEqual(
            get_user_model().objects.using(self.anonymize_db_alias).get(id=a_user.id).shortname,
            '{}'.format(a_user.id))

        # Sanity tests for default database
        self.assertEqual(get_user_model().objects.get(id=d_user.id).shortname, 'testuser')

    @override_settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=True)
    def test_shortname_is_anonymized_with_email_if_django_cradmin_user_email_auth_backend_is_true(self):
        a_user, d_user = self.create_user(shortname='testuser')
        anonymize_database.AnonymizeDatabase(db_alias=self.anonymize_db_alias).anonymize_user()
        self.assertEqual(
            get_user_model().objects.using(self.anonymize_db_alias).get(id=a_user.id).shortname,
            '{}@example.com'.format(a_user.id))

        # Sanity tests for default database
        self.assertEqual(get_user_model().objects.get(id=d_user.id).shortname, 'testuser')

    def test_anonymize_user_email(self):
        a_user, default_db_user = self.create_user()
        a_useremail, d_useremail = self.create_useremail(
            email='testuser@example.com',
            anon_db_user=a_user,
            default_db_user=default_db_user)
        anonymize_database.AnonymizeDatabase(db_alias=self.anonymize_db_alias).anonymize_user()
        self.assertEqual(UserEmail.objects.using(self.anonymize_db_alias).get(id=a_useremail.id).email,
                         '{}_{}@example.com'.format(a_user.id, a_useremail.id))

        # Sanity tests for default database
        self.assertEqual(UserEmail.objects.get(id=d_useremail.id).email, 'testuser@example.com')

    def test_anonymize_user_name(self):
        a_user, d_user = self.create_user(shortname='testuser1')
        a_username, d_username = self.create_username(
            default_db_user=d_user, anon_db_user=a_user, username='testuser1')
        anonymize_database.AnonymizeDatabase(db_alias=self.anonymize_db_alias).anonymize_user()
        self.assertEqual(
            UserName.objects.using(self.anonymize_db_alias).get(id=a_username.id).username,
            '{}_{}'.format(a_user.id, a_username.id))

        # Sanity tests for default database
        self.assertEqual(UserName.objects.get(id=d_username.id).username, 'testuser1')

    def test_anonymize_multiple_users(self):
        a_user1, d_user1 = self.create_user(shortname='testuser1')
        a_user2, d_user2 = self.create_user(shortname='testuser2')
        a_user3, d_user3 = self.create_user(shortname='testuser3')
        anonymize_database.AnonymizeDatabase(db_alias=self.anonymize_db_alias).anonymize_user()
        self.assertEqual(
            get_user_model().objects.using(self.anonymize_db_alias).get(id=a_user1.id).shortname,
            str(a_user1.id))
        self.assertEqual(
            get_user_model().objects.using(self.anonymize_db_alias).get(id=a_user2.id).shortname,
            str(a_user2.id))
        self.assertEqual(
            get_user_model().objects.using(self.anonymize_db_alias).get(id=a_user3.id).shortname,
            str(a_user3.id))

        # Sanity tests for default database
        self.assertEqual(get_user_model().objects.get(id=d_user1.id).shortname, 'testuser1')
        self.assertEqual(get_user_model().objects.get(id=d_user2.id).shortname, 'testuser2')
        self.assertEqual(get_user_model().objects.get(id=d_user3.id).shortname, 'testuser3')

    def test_anonymize_multiple_useremails_for_same_user(self):
        a_user, default_db_user = self.create_user()
        a_useremail1, default_db_useremail1 = self.create_useremail(
            email='testuser1@example.com',
            anon_db_user=a_user,
            default_db_user=default_db_user)
        a_useremail2, default_db_useremail2 = self.create_useremail(
            email='testuser2@example.com',
            anon_db_user=a_user,
            default_db_user=default_db_user)
        anonymize_database.AnonymizeDatabase(db_alias=self.anonymize_db_alias).anonymize_user()
        self.assertTrue(UserEmail.objects.using(self.anonymize_db_alias).filter(email='{}_{}@example.com'.format(
            a_user.id, a_useremail1.id)))
        self.assertTrue(UserEmail.objects.using(self.anonymize_db_alias).filter(email='{}_{}@example.com'.format(
            a_user.id, a_useremail2.id)))

        # Sanity tests for default database
        self.assertEqual(UserEmail.objects.get(id=default_db_useremail1.id).email, 'testuser1@example.com')
        self.assertEqual(UserEmail.objects.get(id=default_db_useremail2.id).email, 'testuser2@example.com')

    def test_anonymize_multiple_user_emails(self):
        a_user1, d_user1 = self.create_user()
        a_user2, d_user2 = self.create_user()
        a_user3, d_user3 = self.create_user()
        a_useremail1, d_useremail1 = self.create_useremail(
            email='testuser1@example.com',
            anon_db_user=a_user1,
            default_db_user=d_user1)
        a_useremail2, d_useremail2 = self.create_useremail(
            email='testuser2@example.com',
            anon_db_user=a_user2,
            default_db_user=d_user2)
        a_useremail3, d_useremail3 = self.create_useremail(
            email='testuser3@example.com',
            anon_db_user=a_user3,
            default_db_user=d_user3)
        anonymize_database.AnonymizeDatabase(db_alias=self.anonymize_db_alias).anonymize_user()
        self.assertEqual(
            UserEmail.objects.using(self.anonymize_db_alias).get(id=a_useremail1.id).email,
            '{}_{}@example.com'.format(a_user1.id, a_useremail1.id))
        self.assertEqual(
            UserEmail.objects.using(self.anonymize_db_alias).get(id=a_useremail2.id).email,
            '{}_{}@example.com'.format(a_user2.id, a_useremail2.id))
        self.assertEqual(
            UserEmail.objects.using(self.anonymize_db_alias).get(id=a_useremail3.id).email,
            '{}_{}@example.com'.format(a_user3.id, a_useremail3.id))

        # Sanity tests for default database
        self.assertEqual(get_user_model().objects.count(), 3)
        self.assertEqual(UserEmail.objects.count(), 3)
        self.assertEqual(UserEmail.objects.get(id=d_useremail1.id).email, 'testuser1@example.com')
        self.assertEqual(UserEmail.objects.get(id=d_useremail2.id).email, 'testuser2@example.com')
        self.assertEqual(UserEmail.objects.get(id=d_useremail3.id).email, 'testuser3@example.com')

    def test_anonymize_multiple_usernames_for_same_user(self):
        a_user, d_user = self.create_user(shortname='testuser')
        a_username1, d_username1 = self.create_username(
            default_db_user=d_user, anon_db_user=a_user, username='testuser1')
        a_username2, d_username2 = self.create_username(
            default_db_user=d_user, anon_db_user=a_user, username='testuser2')
        anonymize_database.AnonymizeDatabase(db_alias=self.anonymize_db_alias).anonymize_user()
        self.assertEqual(
            UserName.objects.using(self.anonymize_db_alias).get(id=a_username1.id).username,
            '{}_{}'.format(a_user.id, a_username1.id))
        self.assertEqual(
            UserName.objects.using(self.anonymize_db_alias).get(id=a_username2.id).username,
            '{}_{}'.format(a_user.id, a_username2.id))

        # Sanity tests for default database
        self.assertEqual(UserName.objects.get(id=d_username1.id).username, 'testuser1')
        self.assertEqual(UserName.objects.get(id=d_username2.id).username, 'testuser2')

    def test_anonymize_multiple_user_names(self):
        a_user1, d_user1 = self.create_user(shortname='testuser1')
        a_user2, d_user2 = self.create_user(shortname='testuser2')
        a_user3, d_user3 = self.create_user(shortname='testuser3')
        a_username1, d_username1 = self.create_username(
            default_db_user=d_user1, anon_db_user=a_user1, username='testuser1')
        a_username2, d_username2 = self.create_username(
            default_db_user=d_user2, anon_db_user=a_user2, username='testuser2')
        a_username3, d_username3 = self.create_username(
            default_db_user=d_user3, anon_db_user=a_user3, username='testuser3')
        anonymize_database.AnonymizeDatabase(db_alias=self.anonymize_db_alias).anonymize_user()
        self.assertEqual(
            UserName.objects.using(self.anonymize_db_alias).get(id=a_username1.id).username,
            '{}_{}'.format(a_user1.id, a_username1.id))
        self.assertEqual(
            UserName.objects.using(self.anonymize_db_alias).get(id=a_username2.id).username,
            '{}_{}'.format(a_user2.id, a_username2.id))
        self.assertEqual(
            UserName.objects.using(self.anonymize_db_alias).get(id=a_username3.id).username,
            '{}_{}'.format(a_user3.id, a_username3.id))

        # Sanity tests for default database
        self.assertEqual(UserName.objects.get(id=d_username1.id).username, 'testuser1')
        self.assertEqual(UserName.objects.get(id=d_username2.id).username, 'testuser2')
        self.assertEqual(UserName.objects.get(id=d_username3.id).username, 'testuser3')


class TestAnonymizeUser(AnonymizeDbTestMixin, test.TestCase):
    anonymize_db_alias = 'anonymize_db'
    multi_db = True

    def test_anonymize_user_shortname(self):
        shortname_to_anonymize = 'testuser'
        self.create_user(shortname=shortname_to_anonymize)
        anonymize_database.AnonymizeDatabase(db_alias=self.anonymize_db_alias, fast=False).anonymize_user()
        anonymized_user = get_user_model().objects.using(self.anonymize_db_alias).get()
        self.assertEqual(len(anonymized_user.shortname),
                         len(shortname_to_anonymize))
        self.assertNotEqual(anonymized_user.shortname, shortname_to_anonymize)

        # Sanity tests for default database
        self.assertEqual(get_user_model().objects.get().shortname, shortname_to_anonymize)

    def test_anonymize_user_fullname(self):
        fullname_to_anonymize = 'Test User'
        self.create_user(fullname=fullname_to_anonymize)
        anonymize_database.AnonymizeDatabase(db_alias=self.anonymize_db_alias, fast=False).anonymize_user()
        anonymized_user = get_user_model().objects.using(self.anonymize_db_alias).get()
        self.assertEqual(len(anonymized_user.fullname),
                         len(fullname_to_anonymize))
        self.assertNotEqual(anonymized_user.fullname,
                            fullname_to_anonymize)

        # Sanity tests for default database
        self.assertEqual(get_user_model().objects.get().fullname, fullname_to_anonymize)

    def test_anonymize_user_lastname(self):
        lastname_to_anonymize = 'Userlastname'
        self.create_user(lastname=lastname_to_anonymize)
        anonymize_database.AnonymizeDatabase(db_alias=self.anonymize_db_alias, fast=False).anonymize_user()
        anonymized_user = get_user_model().objects.using(self.anonymize_db_alias).get()
        self.assertEqual(len(anonymized_user.lastname),
                         len(lastname_to_anonymize))
        self.assertNotEqual(anonymized_user.lastname,
                            lastname_to_anonymize)

        # Sanity tests for default database
        self.assertEqual(get_user_model().objects.get().lastname, lastname_to_anonymize)

    def test_anonymize_useremail(self):
        useremail_to_anonymize = 'testuser@test.com'
        a_user, d_user = self.create_user()
        self.create_useremail(
            email=useremail_to_anonymize,
            anon_db_user=a_user,
            default_db_user=d_user)
        anonymize_database.AnonymizeDatabase(db_alias=self.anonymize_db_alias, fast=False).anonymize_user()
        anonymized_useremail = UserEmail.objects.using(self.anonymize_db_alias).get().email
        self.assertEqual(len(anonymized_useremail.split('@')[0]), len('testuser'))
        self.assertNotEqual(anonymized_useremail.split('@')[0], useremail_to_anonymize)
        self.assertEqual(anonymized_useremail.split('@')[1], 'example.com')

        # Sanity tests for default database
        self.assertEqual(UserEmail.objects.get().email, useremail_to_anonymize)

    def test_anonymize_username(self):
        username_to_anonymize = 'testuser'
        a_user, d_user = self.create_user()
        self.create_username(
            username=username_to_anonymize,
            anon_db_user=a_user,
            default_db_user=d_user)
        anonymize_database.AnonymizeDatabase(db_alias=self.anonymize_db_alias, fast=False).anonymize_user()
        anonymized_username = UserName.objects.using(self.anonymize_db_alias).get().username
        self.assertNotEqual(username_to_anonymize, anonymized_username)
        self.assertEqual(len(anonymized_username), len(username_to_anonymize))

        # Sanity tests for default database
        self.assertEqual(UserName.objects.get().username, username_to_anonymize)


class TestAnonymizeCommentFast(test.TestCase):
    def test_anonymize_comment_text(self):
        comment_text = 'This is a comment.'
        testcomment = mommy.make('devilry_comment.Comment', text=comment_text)
        self.assertEqual(testcomment.text, 'This is a comment.')
        anonymize_database.AnonymizeDatabase(db_alias=self.anonymize_db_alias).anonymize_comments()
        self.assertFalse(Comment.objects.filter(text=comment_text).exists())
        self.assertEqual(Comment.objects.get().text, anonymize_database.lorem_ipsum)

    def test_anonymize_comment_edit_history(self):
        testedithistory = mommy.make('devilry_comment.CommentEditHistory', post_edit_text='Test', pre_edit_text='Tst')
        self.assertEqual(testedithistory.post_edit_text, 'Test')
        self.assertEqual(testedithistory.pre_edit_text, 'Tst')
        anonymize_database.AnonymizeDatabase(db_alias=self.anonymize_db_alias).anonymize_comments()
        self.assertFalse(CommentEditHistory.objects.filter(post_edit_text='Test', pre_edit_text='Tst').exists())
        self.assertEqual(CommentEditHistory.objects.get().post_edit_text, anonymize_database.lorem_ipsum)
        self.assertEqual(CommentEditHistory.objects.get().pre_edit_text, anonymize_database.lorem_ipsum)

    def test_anonymize_comment_file_name(self):
        testcommentfile = mommy.make('devilry_comment.CommentFile', filename='Test.txt')
        self.assertEqual(testcommentfile.filename, 'Test.txt')
        anonymize_database.AnonymizeDatabase(db_alias=self.anonymize_db_alias).anonymize_comments()
        self.assertFalse(CommentFile.objects.filter(filename='Test.txt').exists())
        self.assertEqual(CommentFile.objects.get().filename, str(testcommentfile.id))

    def test_anonymize_group_comment_text(self):
        comment_text = 'This is a comment.'
        testcomment = mommy.make('devilry_group.GroupComment', text=comment_text)
        self.assertEqual(testcomment.text, 'This is a comment.')
        anonymize_database.AnonymizeDatabase(db_alias=self.anonymize_db_alias).anonymize_comments()
        self.assertFalse(Comment.objects.filter(text=comment_text).exists())
        self.assertFalse(GroupComment.objects.filter(text=comment_text).exists())
        self.assertEqual(GroupComment.objects.get().text, anonymize_database.lorem_ipsum)

    def test_anonymize_group_comment_edit_history(self):
        testedithistory = mommy.make('devilry_group.GroupCommentEditHistory', post_edit_text='Test', pre_edit_text='Tst')
        self.assertEqual(testedithistory.post_edit_text, 'Test')
        self.assertEqual(testedithistory.pre_edit_text, 'Tst')
        anonymize_database.AnonymizeDatabase(db_alias=self.anonymize_db_alias).anonymize_comments()
        self.assertFalse(CommentEditHistory.objects.filter(post_edit_text='Test', pre_edit_text='Tst').exists())
        self.assertFalse(GroupCommentEditHistory.objects.filter(post_edit_text='Test', pre_edit_text='Tst').exists())
        self.assertEqual(GroupCommentEditHistory.objects.get().post_edit_text, anonymize_database.lorem_ipsum)
        self.assertEqual(GroupCommentEditHistory.objects.get().pre_edit_text, anonymize_database.lorem_ipsum)
