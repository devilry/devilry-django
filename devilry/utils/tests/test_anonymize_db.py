from django import test
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import override_settings
from model_mommy import mommy

from devilry.devilry_account.models import UserEmail, UserName
from devilry.devilry_comment.models import Comment, CommentEditHistory, CommentFile
from devilry.devilry_group.models import GroupComment, GroupCommentEditHistory
from devilry.utils import anonymize_database


class TestAnonymizeString(test.TestCase):
    # from_db_alias = 'anonymize_db'
    # multi_db = True

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


class TestAnonymizeUserFast(test.TestCase):
    def test_anonymize_user_shortname(self):
        mommy.make(settings.AUTH_USER_MODEL, shortname='testuser')
        self.assertEqual(get_user_model().objects.first().shortname, 'testuser')
        anonymize_database.AnonymizeDatabase(db_alias='test').anonymize_user()
        self.assertEqual(get_user_model().objects.first().shortname,
                         str(get_user_model().objects.get().id))

    @override_settings(DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND=True)
    def test_short_name_is_anonymized_with_email_if_django_cradmin_user_email_auth_backend_is_true(self):
        mommy.make(settings.AUTH_USER_MODEL, shortname='testuser@test.com')
        self.assertEqual(get_user_model().objects.first().shortname, 'testuser@test.com')
        anonymize_database.AnonymizeDatabase(db_alias='test').anonymize_user()
        self.assertEqual(get_user_model().objects.first().shortname,
                         '{}@example.com'.format(get_user_model().objects.get().id))

    def test_anonymize_user_email(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL, shortname='testuser')
        mommy.make('devilry_account.UserEmail', email='testuser@example.com', user=testuser)
        self.assertEqual(UserEmail.objects.get().email, 'testuser@example.com')
        anonymize_database.AnonymizeDatabase(db_alias='test').anonymize_user()
        self.assertEqual(UserEmail.objects.get().email,
                         '{}_{}{}'.format(
                             get_user_model().objects.get().id,
                             UserEmail.objects.get().id,
                             '@example.com'))

    def test_anonymize_user_name(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL, shortname='testuser')
        testusername = mommy.make('devilry_account.UserName', username='testuser', user=testuser)
        self.assertEqual(testusername.username, 'testuser')
        anonymize_database.AnonymizeDatabase(db_alias='test').anonymize_user()
        self.assertEqual(UserName.objects.get().username,
                         '{}_{}'.format(get_user_model().objects.get().id, testusername.id))

    def test_anonymize_multiple_users(self):
        testuser1 = mommy.make(settings.AUTH_USER_MODEL, shortname='testuser1')
        testuser2 = mommy.make(settings.AUTH_USER_MODEL, shortname='testuser2')
        testuser3 = mommy.make(settings.AUTH_USER_MODEL, shortname='testuser3')
        self.assertEqual(get_user_model().objects.filter(shortname='testuser1').count(), 1)
        self.assertEqual(get_user_model().objects.filter(shortname='testuser2').count(), 1)
        self.assertEqual(get_user_model().objects.filter(shortname='testuser3').count(), 1)
        anonymize_database.AnonymizeDatabase(db_alias='test').anonymize_user()
        self.assertEqual(
            get_user_model().objects.get(id=testuser1.id).shortname,
            str(testuser1.id))
        self.assertEqual(
            get_user_model().objects.get(id=testuser2.id).shortname,
            str(testuser2.id))
        self.assertEqual(
            get_user_model().objects.get(id=testuser3.id).shortname,
            str(testuser3.id))

    def test_anonymize_multiple_useremails_for_same_user(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL, shortname='testuser')
        testuseremail1 = mommy.make('devilry_account.UserEmail', email='testuser1@example.com', user=testuser)
        testuseremail2 = mommy.make('devilry_account.UserEmail', email='testuser2@example.com', user=testuser)
        self.assertTrue(UserEmail.objects.filter(email='testuser1@example.com').exists())
        self.assertTrue(UserEmail.objects.filter(email='testuser2@example.com').exists())
        anonymize_database.AnonymizeDatabase(db_alias='test').anonymize_user()
        self.assertTrue(UserEmail.objects.filter(email='{}_{}@example.com'.format(testuser.id, testuseremail1.id)))
        self.assertTrue(UserEmail.objects.filter(email='{}_{}@example.com'.format(testuser.id, testuseremail2.id)))

    def test_anonymize_multiple_user_emails(self):
        testemail1 = mommy.make('devilry_account.UserEmail', email='testemail1@example.com')
        testemail2 = mommy.make('devilry_account.UserEmail', email='testemail2@example.com')
        testemail3 = mommy.make('devilry_account.UserEmail', email='testemail3@example.com')
        self.assertEqual(UserEmail.objects.filter(email='testemail1@example.com').count(), 1)
        self.assertEqual(UserEmail.objects.filter(email='testemail2@example.com').count(), 1)
        self.assertEqual(UserEmail.objects.filter(email='testemail3@example.com').count(), 1)
        anonymize_database.AnonymizeDatabase(db_alias='test').anonymize_user()
        self.assertEqual(
            UserEmail.objects.get(id=testemail1.id).email,
            '{}_{}@example.com'.format(testemail1.user.id, testemail1.id))
        self.assertEqual(
            UserEmail.objects.get(id=testemail2.id).email,
            '{}_{}@example.com'.format(testemail2.user.id, testemail2.id))
        self.assertEqual(
            UserEmail.objects.get(id=testemail3.id).email,
            '{}_{}@example.com'.format(testemail3.user.id, testemail3.id))

    def test_anonymize_multiple_usernames_for_same_user(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL, shortname='testuser')
        testusername1 = mommy.make('devilry_account.UserName', username='testuser1', user=testuser)
        testusername2 = mommy.make('devilry_account.UserName', username='testuser2', user=testuser)
        self.assertTrue(UserName.objects.filter(username='testuser1').exists())
        self.assertTrue(UserName.objects.filter(username='testuser2').exists())
        anonymize_database.AnonymizeDatabase(db_alias='test').anonymize_user()
        self.assertTrue(UserName.objects.filter(username='{}_{}'.format(testuser.id, testusername1.id)))
        self.assertTrue(UserName.objects.filter(username='{}_{}'.format(testuser.id, testusername2.id)))

    def test_anonymize_multiple_user_names(self):
        testusername1 = mommy.make('devilry_account.UserName', username='testusername1')
        testusername2 = mommy.make('devilry_account.UserName', username='testusername2')
        testusername3 = mommy.make('devilry_account.UserName', username='testusername3')
        self.assertEqual(UserName.objects.filter(username='testusername1').count(), 1)
        self.assertEqual(UserName.objects.filter(username='testusername2').count(), 1)
        self.assertEqual(UserName.objects.filter(username='testusername3').count(), 1)
        anonymize_database.AnonymizeDatabase(db_alias='test').anonymize_user()
        self.assertEqual(
            UserName.objects.get(id=testusername1.id).username,
            '{}_{}'.format(testusername1.user.id, testusername1.id))
        self.assertEqual(
            UserName.objects.get(id=testusername2.id).username,
            '{}_{}'.format(testusername2.user.id, testusername2.id))
        self.assertEqual(
            UserName.objects.get(id=testusername3.id).username,
            '{}_{}'.format(testusername3.user.id, testusername3.id))


class TestAnonymizeUser(test.TestCase):
    def test_anonymize_user_shortname(self):
        shortname_to_anonymize = 'testuser'
        mommy.make(settings.AUTH_USER_MODEL, shortname=shortname_to_anonymize)
        self.assertEqual(get_user_model().objects.first().shortname, shortname_to_anonymize)
        anonymize_database.AnonymizeDatabase(db_alias='test', fast=False).anonymize_user()
        anonymized_user = get_user_model().objects.get()
        self.assertEqual(len(anonymized_user.shortname),
                         len(shortname_to_anonymize))

    def test_anonymize_user_fullname(self):
        fullname_to_anonymize = 'Test User'
        mommy.make(settings.AUTH_USER_MODEL, fullname=fullname_to_anonymize)
        self.assertEqual(get_user_model().objects.first().fullname, fullname_to_anonymize)
        anonymize_database.AnonymizeDatabase(db_alias='test', fast=False).anonymize_user()
        anonymized_user = get_user_model().objects.get()
        self.assertEqual(len(anonymized_user.fullname),
                         len(fullname_to_anonymize))

    def test_anonymize_user_lastname(self):
        lastname_to_anonymize = 'Userlastname'
        mommy.make(settings.AUTH_USER_MODEL, lastname=lastname_to_anonymize)
        self.assertEqual(get_user_model().objects.first().lastname, lastname_to_anonymize)
        anonymize_database.AnonymizeDatabase(db_alias='test', fast=False).anonymize_user()
        anonymized_user = get_user_model().objects.get()
        self.assertEqual(len(anonymized_user.lastname),
                         len(lastname_to_anonymize))

    def test_anonymize_useremail(self):
        useremail_to_anonymize = 'testuser@test.com'
        mommy.make('devilry_account.UserEmail', email=useremail_to_anonymize)
        self.assertEqual(UserEmail.objects.get().email, useremail_to_anonymize)
        anonymize_database.AnonymizeDatabase(db_alias='test', fast=False).anonymize_user()
        anonymized_useremail = UserEmail.objects.get().email
        self.assertEqual(len(anonymized_useremail.split('@')[0]), len('testuser'))
        self.assertEqual(len(anonymized_useremail.split('@')[1]), len('example.com'))

    def test_anonymize_username(self):
        username_to_anonymize = 'testuser'
        mommy.make('devilry_account.UserName', username=username_to_anonymize)
        self.assertEqual(UserName.objects.get().username, username_to_anonymize)
        anonymize_database.AnonymizeDatabase(db_alias='test', fast=False).anonymize_user()
        anonymized_username = UserName.objects.get().username
        self.assertNotEqual(username_to_anonymize, anonymized_username)
        self.assertEqual(len(anonymized_username), len(username_to_anonymize))


class TestAnonymizeCommentFast(test.TestCase):
    def test_anonymize_comment_text(self):
        comment_text = 'This is a comment.'
        testcomment = mommy.make('devilry_comment.Comment', text=comment_text)
        self.assertEqual(testcomment.text, 'This is a comment.')
        anonymize_database.AnonymizeDatabase(db_alias='test').anonymize_comments()
        self.assertFalse(Comment.objects.filter(text=comment_text).exists())
        self.assertEqual(Comment.objects.get().text, anonymize_database.lorem_ipsum)

    def test_anonymize_comment_edit_history(self):
        testedithistory = mommy.make('devilry_comment.CommentEditHistory', post_edit_text='Test', pre_edit_text='Tst')
        self.assertEqual(testedithistory.post_edit_text, 'Test')
        self.assertEqual(testedithistory.pre_edit_text, 'Tst')
        anonymize_database.AnonymizeDatabase(db_alias='test').anonymize_comments()
        self.assertFalse(CommentEditHistory.objects.filter(post_edit_text='Test', pre_edit_text='Tst').exists())
        self.assertEqual(CommentEditHistory.objects.get().post_edit_text, anonymize_database.lorem_ipsum)
        self.assertEqual(CommentEditHistory.objects.get().pre_edit_text, anonymize_database.lorem_ipsum)

    def test_anonymize_comment_file_name(self):
        testcommentfile = mommy.make('devilry_comment.CommentFile', filename='Test.txt')
        self.assertEqual(testcommentfile.filename, 'Test.txt')
        anonymize_database.AnonymizeDatabase(db_alias='test').anonymize_comments()
        self.assertFalse(CommentFile.objects.filter(filename='Test.txt').exists())
        self.assertEqual(CommentFile.objects.get().filename, str(testcommentfile.id))

    def test_anonymize_group_comment_text(self):
        comment_text = 'This is a comment.'
        testcomment = mommy.make('devilry_group.GroupComment', text=comment_text)
        self.assertEqual(testcomment.text, 'This is a comment.')
        anonymize_database.AnonymizeDatabase(db_alias='test').anonymize_comments()
        self.assertFalse(Comment.objects.filter(text=comment_text).exists())
        self.assertFalse(GroupComment.objects.filter(text=comment_text).exists())
        self.assertEqual(GroupComment.objects.get().text, anonymize_database.lorem_ipsum)

    def test_anonymize_group_comment_edit_history(self):
        testedithistory = mommy.make('devilry_group.GroupCommentEditHistory', post_edit_text='Test', pre_edit_text='Tst')
        self.assertEqual(testedithistory.post_edit_text, 'Test')
        self.assertEqual(testedithistory.pre_edit_text, 'Tst')
        anonymize_database.AnonymizeDatabase(db_alias='test').anonymize_comments()
        self.assertFalse(CommentEditHistory.objects.filter(post_edit_text='Test', pre_edit_text='Tst').exists())
        self.assertFalse(GroupCommentEditHistory.objects.filter(post_edit_text='Test', pre_edit_text='Tst').exists())
        self.assertEqual(GroupCommentEditHistory.objects.get().post_edit_text, anonymize_database.lorem_ipsum)
        self.assertEqual(GroupCommentEditHistory.objects.get().pre_edit_text, anonymize_database.lorem_ipsum)
