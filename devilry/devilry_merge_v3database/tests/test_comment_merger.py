import os
import shutil

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from model_mommy import mommy

from devilry.devilry_group import models as group_models
from devilry.devilry_comment import models as comment_models
from devilry.devilry_merge_v3database.models import TempMergeId

from devilry.devilry_merge_v3database.utils import comment_merger
from devilry.devilry_merge_v3database.tests.utils import MergerTestHelper


class CommentMergersHelperMixin:
    """
    Helper mixin for Comment related mergers.
    """
    def create_temp_merge_id(self, from_id, to_id):
        mommy.make('devilry_merge_v3database.TempMergeId',
                   from_id=from_id,
                   to_id=to_id,
                   model_name='devilry_comment_comment')

    def create_comment(self, user, comment_kwargs, db_alias='default'):
        if not comment_kwargs:
            comment_kwargs = {}
        comment = mommy.prepare('devilry_comment.Comment', user=user, **comment_kwargs)
        comment.save(using=db_alias)
        return comment

    def create_for_default_db(self, user_kwargs=None, with_user=False, comment_kwargs=None, with_comment=False):
        if with_user:
            user = self.get_or_create_user(user_kwargs=user_kwargs)
        else:
            user = None
        if with_comment:
            if not comment_kwargs:
                comment_kwargs = {'text': 'default'}
            return self.create_comment(user=user, comment_kwargs=comment_kwargs)
        return None

    def create_for_migrate_db(self, user_kwargs=None, with_user=False, comment_kwargs=None):
        if with_user:
            if not user_kwargs:
                user_kwargs = {'shortname': 'migrate_user'}
            user = self.get_or_create_user(user_kwargs=user_kwargs, db_alias=self.from_db_alias)
        else:
            user = None
        if not comment_kwargs:
            comment_kwargs = {'text': 'migrate'}
        return self.create_comment(user=user, comment_kwargs=comment_kwargs, db_alias=self.from_db_alias)


class TestCommentMerger(CommentMergersHelperMixin, MergerTestHelper):
    from_db_alias = 'migrate_from'
    multi_db = True

    def test_database_sanity(self):
        # Default database data
        self.create_for_default_db(with_user=True, with_comment=True)

        # Migrate database data
        self.create_for_migrate_db(with_user=True)

        # Test default database
        self.assertEqual(comment_models.Comment.objects.count(), 1)
        self.assertEqual(
            comment_models.Comment.objects.get().text, 'default')
        self.assertEqual(comment_models.Comment.objects.get().user.shortname, 'default_user')

        # Test migrate database
        self.assertEqual(comment_models.Comment.objects.using(self.from_db_alias).count(), 1)
        self.assertEqual(
            comment_models.Comment.objects.using(self.from_db_alias).get().text, 'migrate')
        self.assertEqual(
            comment_models.Comment.objects.using(self.from_db_alias).select_related('user')
                .get().user.shortname, 'migrate_user')

    def test_comment_migrated_sanity(self):
        # Default database data
        self.create_for_default_db(with_user=True, user_kwargs={'shortname': 'migrate_user'})

        # Migrate database data
        self.create_for_migrate_db(with_user=True)

        self.assertEqual(comment_models.Comment.objects.count(), 0)
        self.assertEqual(get_user_model().objects.count(), 1)

        comment_merger.CommentMerger(from_db_alias=self.from_db_alias, transaction=True).run()

        self.assertEqual(comment_models.Comment.objects.count(), 1)
        self.assertEqual(get_user_model().objects.count(), 1)
        self.assertEqual(comment_models.Comment.objects.get().user, get_user_model().objects.get())

    def test_multiple_comments_migrated_for_same_user(self):
        # Default database data
        self.create_for_default_db(with_user=True, user_kwargs={'shortname': 'migrate_user'})

        # Migrate database data
        self.create_for_migrate_db(with_user=True, user_kwargs={'shortname': 'migrate_user'},
                                   comment_kwargs={'text': 'migrated 1'})
        self.create_for_migrate_db(with_user=True, user_kwargs={'shortname': 'migrate_user'},
                                   comment_kwargs={'text': 'migrated 2'})
        self.create_for_migrate_db(with_user=True, user_kwargs={'shortname': 'migrate_user'},
                                   comment_kwargs={'text': 'migrated 3'})
        self.create_for_migrate_db(with_user=True, user_kwargs={'shortname': 'migrate_user'},
                                   comment_kwargs={'text': 'migrated 4'})

        self.assertEqual(comment_models.Comment.objects.count(), 0)
        self.assertEqual(get_user_model().objects.count(), 1)

        comment_merger.CommentMerger(from_db_alias=self.from_db_alias, transaction=True).run()

        self.assertEqual(get_user_model().objects.count(), 1)
        self.assertEqual(comment_models.Comment.objects.count(), 4)
        self.assertEqual(comment_models.Comment.objects.filter(user__shortname='migrate_user').count(), 4)
        self.assertEqual(comment_models.Comment.objects.filter(text='migrated 1').count(), 1)
        self.assertEqual(comment_models.Comment.objects.filter(text='migrated 2').count(), 1)
        self.assertEqual(comment_models.Comment.objects.filter(text='migrated 3').count(), 1)
        self.assertEqual(comment_models.Comment.objects.filter(text='migrated 4').count(), 1)

    def test_multiple_comment_for_multiple_users_migrated(self):
        # Default database data
        self.create_for_default_db(with_user=True, user_kwargs={'shortname': 'migrate_user1'})
        self.create_for_default_db(with_user=True, user_kwargs={'shortname': 'migrate_user2'})
        self.create_for_default_db(with_user=True, user_kwargs={'shortname': 'migrate_user3'})

        # Migrate database data
        self.create_for_migrate_db(with_user=True, user_kwargs={'shortname': 'migrate_user1'},
                                   comment_kwargs={'text': 'comment 1'})
        self.create_for_migrate_db(with_user=True, user_kwargs={'shortname': 'migrate_user1'},
                                   comment_kwargs={'text': 'comment 2'})
        self.create_for_migrate_db(with_user=True, user_kwargs={'shortname': 'migrate_user2'},
                                   comment_kwargs={'text': 'comment 3'})
        self.create_for_migrate_db(with_user=True, user_kwargs={'shortname': 'migrate_user3'},
                                   comment_kwargs={'text': 'comment 4'})
        self.create_for_migrate_db(with_user=True, user_kwargs={'shortname': 'migrate_user3'},
                                   comment_kwargs={'text': 'comment 5'})
        self.create_for_migrate_db(with_user=True, user_kwargs={'shortname': 'migrate_user3'},
                                   comment_kwargs={'text': 'comment 6'})

        self.assertEqual(comment_models.Comment.objects.count(), 0)
        self.assertEqual(get_user_model().objects.count(), 3)

        comment_merger.CommentMerger(from_db_alias=self.from_db_alias, transaction=True).run()

        self.assertEqual(comment_models.Comment.objects.count(), 6)

        # Check correct comments migrated to migrate_user1
        migrate_user1_comment_texts = [
            comment.text for comment in comment_models.Comment.objects.filter(user__shortname='migrate_user1')]
        self.assertEqual(len(migrate_user1_comment_texts), 2)
        self.assertIn('comment 1', migrate_user1_comment_texts)
        self.assertIn('comment 2', migrate_user1_comment_texts)

        # Check correct comments migrated to migrate_user2
        migrate_user2_comment_texts = [
            comment.text for comment in comment_models.Comment.objects.filter(user__shortname='migrate_user2')]
        self.assertEqual(len(migrate_user2_comment_texts), 1)
        self.assertIn('comment 3', migrate_user2_comment_texts)

        # Check correct comments migrated to migrate_user3
        migrate_user3_comment_texts = [
            comment.text for comment in comment_models.Comment.objects.filter(user__shortname='migrate_user3')]
        self.assertEqual(len(migrate_user3_comment_texts), 3)
        self.assertIn('comment 4', migrate_user3_comment_texts)
        self.assertIn('comment 5', migrate_user3_comment_texts)
        self.assertIn('comment 6', migrate_user3_comment_texts)

    def test_comment_can_be_migrated_without_user(self):
        # Migrate database data
        self.create_for_migrate_db()

        self.assertEqual(comment_models.Comment.objects.count(), 0)
        comment_merger.CommentMerger(from_db_alias=self.from_db_alias, transaction=True).run()
        self.assertEqual(comment_models.Comment.objects.count(), 1)
        self.assertIsNone(comment_models.Comment.objects.get().user)
        self.assertEqual(comment_models.Comment.objects.get().text, 'migrate')

    def test_comment_migrated_temp_merge_id_created(self):
        # Default database data
        self.create_for_default_db(with_user=True)

        # Migrate database data
        self.create_for_migrate_db(with_user=True, comment_kwargs={'id': 512})

        self.assertEqual(comment_models.Comment.objects.count(), 0)
        self.assertEqual(TempMergeId.objects.count(), 0)

        comment_merger.CommentMerger(from_db_alias=self.from_db_alias, transaction=True).run()

        self.assertEqual(comment_models.Comment.objects.count(), 1)
        self.assertEqual(TempMergeId.objects.count(), 1)
        temp_merge_id = TempMergeId.objects.get()
        self.assertEqual(temp_merge_id.to_id, comment_models.Comment.objects.get().id)
        self.assertEqual(temp_merge_id.from_id, 512)
        self.assertEqual(temp_merge_id.model_name, 'devilry_comment_comment')


class TestCommentFileMerger(CommentMergersHelperMixin, MergerTestHelper):
    from_db_alias = 'migrate_from'
    multi_db = True

    def tearDown(self):
        # Ignores errors if the path is not created.
        shutil.rmtree('devilry_testfiles/filestore/', ignore_errors=True)

    def create_comment_file(self, comment, comment_file_kwargs, db_alias='default'):
        if not comment_file_kwargs:
            comment_file_kwargs = {}
        file_content = comment_file_kwargs.pop('file_content', 'Test content')
        comment_file = mommy.prepare('devilry_comment.CommentFile', comment=comment, **comment_file_kwargs)
        comment_file.save(using=db_alias)
        comment_file.file.save('testfile.txt', ContentFile(file_content))
        comment_file.save(using=db_alias)

    def create_for_default_db(self, with_comment_file=False, comment_file_kwargs=None,
                              **default_db_kwargs):
        comment = super(TestCommentFileMerger, self).create_for_default_db(with_comment=True, **default_db_kwargs)
        if with_comment_file:
            if not comment_file_kwargs:
                comment_file_kwargs = {}
            self.create_comment_file(comment=comment, comment_file_kwargs=comment_file_kwargs)
        return comment

    def create_for_migrate_db(self, comment_file_kwargs=None, **migrate_db_kwargs):
        comment = super(TestCommentFileMerger, self).create_for_migrate_db(**migrate_db_kwargs)
        if not comment_file_kwargs:
            comment_file_kwargs = {}
        self.create_comment_file(comment=comment, comment_file_kwargs=comment_file_kwargs, db_alias=self.from_db_alias)
        return comment

    def test_database_sanity(self):
        # Default database data
        self.create_for_default_db(with_user=True, with_comment_file=True,
                                   comment_file_kwargs={'file_content': 'Default content'})

        # Migrate database data
        self.create_for_migrate_db(with_user=True, comment_kwargs={'id': 512},
                                   comment_file_kwargs={'file_content': 'Migrate content'})

        # Test default database
        self.assertEqual(comment_models.CommentFile.objects.count(), 1)
        self.assertTrue(os.path.exists(comment_models.CommentFile.objects.get().file.path))
        self.assertEqual(comment_models.CommentFile.objects.get().file.file.read(),
                         'Default content')

        # Test migrate database
        self.assertEqual(comment_models.CommentFile.objects.using(self.from_db_alias).count(), 1)
        self.assertTrue(os.path.exists(comment_models.CommentFile.objects.using(self.from_db_alias).get().file.path))
        self.assertEqual(comment_models.CommentFile.objects.using(self.from_db_alias).get().file.file.read(),
                         'Migrate content')

    def test_temp_merge_id_for_comments_does_not_exist(self):
        # Migrate database data
        self.create_for_migrate_db(with_user=True, comment_kwargs={'id': 512},
                                   comment_file_kwargs={'file_content': 'Migrate content'})
        with self.assertRaisesMessage(ValueError, 'Comments must be imported before CommentFiles.'):
            comment_merger.CommentFileMerger(
                from_db_alias=self.from_db_alias, migrate_media_root=settings.MEDIA_ROOT, transaction=True).run()

    def test_temp_merge_id_does_not_exist_for_comment(self):
        # Migrate database data
        self.create_for_migrate_db(with_user=True, comment_kwargs={'id': 512},
                                   comment_file_kwargs={'file_content': 'Migrate content'})

        # Create TempMergeId
        self.create_temp_merge_id(from_id=comment_models.Comment.objects.using(self.from_db_alias).get().id,
                                    to_id=12)

        with self.assertRaisesMessage(ValueError, 'Comments must be imported before CommentFiles.'):
            comment_merger.CommentFileMerger(
                from_db_alias=self.from_db_alias, migrate_media_root=settings.MEDIA_ROOT, transaction=True).run()

    def test_migrate_comment_file(self):
        # Default database data
        self.create_for_default_db(with_user=True)

        # Migrate database data
        self.create_for_migrate_db(with_user=True, comment_kwargs={'id': 512},
                                     comment_file_kwargs={'file_content': 'Migrate content'})

        # Create TempMergeId for Comment
        self.create_temp_merge_id(from_id=comment_models.Comment.objects.using(self.from_db_alias).get().id,
                                  to_id=comment_models.Comment.objects.get().id)

        self.assertEqual(comment_models.Comment.objects.count(), 1)
        self.assertEqual(comment_models.CommentFile.objects.count(), 0)

        comment_merger.CommentFileMerger(
            from_db_alias=self.from_db_alias, migrate_media_root=settings.MEDIA_ROOT, transaction=True).run()

        self.assertEqual(comment_models.Comment.objects.count(), 1)
        self.assertEqual(comment_models.CommentFile.objects.count(), 1)
        self.assertTrue(os.path.exists(comment_models.CommentFile.objects.get().file.path))
        self.assertEqual(comment_models.CommentFile.objects.get().file.file.read(),
                         'Migrate content')

    def test_migrate_comment_with_multiple_files(self):
        # Default database data
        self.create_for_default_db(with_user=True)

        # Migrate database data
        self.create_for_migrate_db(with_user=True, comment_kwargs={'id': 512},
                                   comment_file_kwargs={'file_content': 'Migrate content1'})
        migrate_comment = comment_models.Comment.objects.using(self.from_db_alias).get()
        self.create_comment_file(comment=migrate_comment,
                                 comment_file_kwargs={'file_content': 'Migrate content2'}, db_alias=self.from_db_alias)
        self.create_comment_file(comment=migrate_comment,
                                 comment_file_kwargs={'file_content': 'Migrate content3'}, db_alias=self.from_db_alias)

        # Create TempMergeId for Comment
        self.create_temp_merge_id(from_id=comment_models.Comment.objects.using(self.from_db_alias).get().id,
                                    to_id=comment_models.Comment.objects.get().id)

        self.assertEqual(comment_models.Comment.objects.count(), 1)
        self.assertEqual(comment_models.CommentFile.objects.count(), 0)

        comment_merger.CommentFileMerger(
            from_db_alias=self.from_db_alias, migrate_media_root=settings.MEDIA_ROOT, transaction=True).run()

        self.assertEqual(comment_models.Comment.objects.count(), 1)
        self.assertEqual(comment_models.CommentFile.objects.count(), 3)
        comment = comment_models.Comment.objects.get()
        self.assertEqual(comment_models.CommentFile.objects.filter(comment=comment).count(), 3)

        for comment_file in comment_models.CommentFile.objects.all():
            self.assertTrue(os.path.exists(comment_file.file.path))

        comment_content = [comment_file.file.file.read() for comment_file in comment_models.CommentFile.objects.all()]
        self.assertIn('Migrate content1', comment_content)
        self.assertIn('Migrate content2', comment_content)
        self.assertIn('Migrate content3', comment_content)

    def test_migrate_comment_files_for_multiple_comments(self):
        # Default database data
        default_comment1 = self.create_for_default_db(with_user=True)
        default_comment2 = self.create_for_default_db(with_user=True)
        default_comment3 = self.create_for_default_db(with_user=True)

        # Migrate database data
        migrate_comment1 = self.create_for_migrate_db(with_user=True, comment_kwargs={'id': 512},
                                                      comment_file_kwargs={'file_content': 'Migrate content 512'})
        migrate_comment2 = self.create_for_migrate_db(with_user=True, comment_kwargs={'id': 513},
                                                      comment_file_kwargs={'file_content': 'Migrate content 513'})
        migrate_comment3 = self.create_for_migrate_db(with_user=True, comment_kwargs={'id': 514},
                                                      comment_file_kwargs={'file_content': 'Migrate content 514'})

        # Create temp merge ids for comments
        self.create_temp_merge_id(from_id=migrate_comment1.id, to_id=default_comment1.id)
        self.create_temp_merge_id(from_id=migrate_comment2.id, to_id=default_comment2.id)
        self.create_temp_merge_id(from_id=migrate_comment3.id, to_id=default_comment3.id)

        self.assertEqual(comment_models.Comment.objects.count(), 3)
        self.assertEqual(comment_models.CommentFile.objects.count(), 0)

        comment_merger.CommentFileMerger(
            from_db_alias=self.from_db_alias, migrate_media_root=settings.MEDIA_ROOT, transaction=True).run()

        self.assertEqual(comment_models.Comment.objects.count(), 3)
        self.assertEqual(comment_models.CommentFile.objects.count(), 3)

        comment_file_512 = comment_models.CommentFile.objects.get(id=TempMergeId.objects.get(from_id=512).to_id)
        comment_file_513 = comment_models.CommentFile.objects.get(id=TempMergeId.objects.get(from_id=513).to_id)
        comment_file_514 = comment_models.CommentFile.objects.get(id=TempMergeId.objects.get(from_id=514).to_id)

        self.assertTrue(os.path.exists(comment_file_512.file.path))
        self.assertEqual(comment_file_512.file.file.read(), 'Migrate content 512')

        self.assertTrue(os.path.exists(comment_file_513.file.path))
        self.assertEqual(comment_file_513.file.file.read(), 'Migrate content 513')

        self.assertTrue(os.path.exists(comment_file_514.file.path))
        self.assertEqual(comment_file_514.file.file.read(), 'Migrate content 514')


class TestCommentEditHistoryMerger(CommentMergersHelperMixin, MergerTestHelper):
    from_db_alias = 'migrate_from'
    multi_db = True

    def create_comment_edit_history(self, comment, edit_history_kwargs, db_alias='default'):
        if not edit_history_kwargs:
            edit_history_kwargs = {}
        edit_history = mommy.prepare('devilry_comment.CommentEditHistory', comment=comment, **edit_history_kwargs)
        edit_history.save(using=db_alias)

    def create_for_default_db(self, with_edit_history=False, edit_history_kwargs=None, **default_db_kwargs):
        comment = super(TestCommentEditHistoryMerger, self)\
            .create_for_default_db(with_comment=True, **default_db_kwargs)
        if with_edit_history:
            if not edit_history_kwargs:
                edit_history_kwargs = {}
            self.create_comment_edit_history(comment=comment, edit_history_kwargs=edit_history_kwargs)
        return comment

    def create_for_migrate_db(self, edit_history_kwargs=None, **migrate_db_kwargs):
        comment = super(TestCommentEditHistoryMerger, self).create_for_migrate_db(**migrate_db_kwargs)
        if not edit_history_kwargs:
            edit_history_kwargs = {}
        self.create_comment_edit_history(
            comment=comment, edit_history_kwargs=edit_history_kwargs, db_alias=self.from_db_alias)
        return comment

    def test_database_sanity(self):
        # Default database data
        self.create_for_default_db(with_user=True, with_edit_history=True,
                                   edit_history_kwargs={'post_edit_text': 'default'})

        # Migrate database data
        self.create_for_migrate_db(with_user=True,
                                   edit_history_kwargs={'post_edit_text': 'migrate'})

        # Test default database
        self.assertEqual(comment_models.CommentEditHistory.objects.count(), 1)
        self.assertEqual(comment_models.CommentEditHistory.objects.get().post_edit_text, 'default')

        # Test migrate database
        self.assertEqual(comment_models.CommentEditHistory.objects.using(self.from_db_alias).count(), 1)
        self.assertEqual(comment_models.CommentEditHistory.objects.using(self.from_db_alias).get().post_edit_text,
                         'migrate')

    def test_temp_merge_id_does_not_exist(self):
        # Migrate database data
        self.create_for_migrate_db(with_user=True,
                                   edit_history_kwargs={'post_edit_text': 'migrate'})
        with self.assertRaisesMessage(ValueError, 'Comments must be imported before CommentEditHistory'):
            comment_merger.CommentEditHistoryMerger(
                from_db_alias=self.from_db_alias, transaction=True).run()

    def test_temp_merge_id_for_comment_does_not_exist(self):
        # Migrate database data
        self.create_for_migrate_db(with_user=True,
                                   edit_history_kwargs={'post_edit_text': 'migrate'})

        # Create TempMergeId
        self.create_temp_merge_id(from_id=comment_models.Comment.objects.using(self.from_db_alias).get().id,
                                  to_id=12)

        with self.assertRaisesMessage(ValueError, 'Comments must be imported before CommentEditHistory'):
            comment_merger.CommentEditHistoryMerger(
                from_db_alias=self.from_db_alias, transaction=True).run()

    def test_migrate_comment_edit_history(self):
        # Default database data
        self.create_for_default_db(with_user=True)

        # Migrate database data
        self.create_for_migrate_db(with_user=True,
                                   edit_history_kwargs={'post_edit_text': 'migrate'})

        # Create TempMergeId for Comment
        self.create_temp_merge_id(from_id=comment_models.Comment.objects.using(self.from_db_alias).get().id,
                                  to_id=comment_models.Comment.objects.get().id)

        self.assertEqual(comment_models.Comment.objects.count(), 1)
        self.assertEqual(comment_models.CommentEditHistory.objects.count(), 0)

        comment_merger.CommentEditHistoryMerger(
            from_db_alias=self.from_db_alias, transaction=True).run()

        self.assertEqual(comment_models.Comment.objects.count(), 1)
        self.assertEqual(comment_models.CommentEditHistory.objects.count(), 1)
        self.assertEqual(comment_models.CommentEditHistory.objects.get().post_edit_text, 'migrate')

    def test_migrate_multiple_comment_edit_history_entries_for_same_comment(self):
        # Default database data
        self.create_for_default_db(with_user=True)

        # Migrate database data
        comment = self.create_for_migrate_db(with_user=True, edit_history_kwargs={'post_edit_text': 'migrate1'})
        self.create_comment_edit_history(comment=comment, edit_history_kwargs={'post_edit_text': 'migrate2'},
                                         db_alias=self.from_db_alias)
        self.create_comment_edit_history(comment=comment, edit_history_kwargs={'post_edit_text': 'migrate3'},
                                         db_alias=self.from_db_alias)

        # Create TempMergeIds for Comments
        self.create_temp_merge_id(
            from_id=comment_models.Comment.objects.using(self.from_db_alias).get().id,
            to_id=comment_models.Comment.objects.get().id)

        self.assertEqual(comment_models.Comment.objects.count(), 1)
        self.assertEqual(comment_models.CommentEditHistory.objects.count(), 0)

        comment_merger.CommentEditHistoryMerger(
            from_db_alias=self.from_db_alias, transaction=True).run()

        self.assertEqual(comment_models.Comment.objects.count(), 1)
        self.assertEqual(comment_models.CommentEditHistory.objects.count(), 3)
        self.assertEqual(
            comment_models.CommentEditHistory.objects.filter(comment=comment_models.Comment.objects.get()).count(),
            3)
        edit_history_texts = [edit_history.post_edit_text for edit_history
                              in comment_models.CommentEditHistory.objects.all()]
        self.assertEqual(len(edit_history_texts), 3)
        self.assertIn('migrate1', edit_history_texts)
        self.assertIn('migrate2', edit_history_texts)
        self.assertIn('migrate3', edit_history_texts)

    def test_migrate_multiple_comment_edit_history_entries_for_multiple_comments(self):
        # Default database data
        default_comment1 = self.create_for_default_db(with_user=True)
        default_comment2 = self.create_for_default_db(with_user=True)
        default_comment3 = self.create_for_default_db(with_user=True)

        # Migrate database data
        migrate_comment1 = self.create_for_migrate_db(with_user=True,
                                                      edit_history_kwargs={'post_edit_text': 'migrate1'})
        migrate_comment2 = self.create_for_migrate_db(with_user=True,
                                                      edit_history_kwargs={'post_edit_text': 'migrate2'})
        migrate_comment3 = self.create_for_migrate_db(with_user=True,
                                                      edit_history_kwargs={'post_edit_text': 'migrate3'})

        # Create TempMergeIds for Comments
        self.create_temp_merge_id(
            from_id=migrate_comment1.id,
            to_id=default_comment1.id)
        self.create_temp_merge_id(
            from_id=migrate_comment2.id,
            to_id=default_comment2.id)
        self.create_temp_merge_id(
            from_id=migrate_comment3.id,
            to_id=default_comment3.id)

        self.assertEqual(comment_models.Comment.objects.count(), 3)
        self.assertEqual(comment_models.CommentEditHistory.objects.count(), 0)

        comment_merger.CommentEditHistoryMerger(
            from_db_alias=self.from_db_alias, transaction=True).run()

        self.assertEqual(comment_models.Comment.objects.count(), 3)
        self.assertEqual(comment_models.CommentEditHistory.objects.count(), 3)

        self.assertEqual(comment_models.CommentEditHistory.objects.filter(comment=default_comment1).count(), 1)
        self.assertEqual(comment_models.CommentEditHistory.objects.filter(comment=default_comment2).count(), 1)
        self.assertEqual(comment_models.CommentEditHistory.objects.filter(comment=default_comment3).count(), 1)

        self.assertEqual(
            comment_models.CommentEditHistory.objects.filter(comment=default_comment1).get().post_edit_text,
            'migrate1')
        self.assertEqual(
            comment_models.CommentEditHistory.objects.filter(comment=default_comment2).get().post_edit_text,
            'migrate2')
        self.assertEqual(
            comment_models.CommentEditHistory.objects.filter(comment=default_comment3).get().post_edit_text,
            'migrate3')


class TestGroupCommentMerger(MergerTestHelper):
    from_db_alias = 'migrate_from'
    multi_db = True

    def create_group_comment(self, feedback_set, group_comment_kwargs, db_alias='default'):
        if not group_comment_kwargs:
            group_comment_kwargs = {}
        group_comment = mommy.prepare('devilry_group.GroupComment', feedback_set=feedback_set, **group_comment_kwargs)
        group_comment.save(using=db_alias)

    def __create_for_default_db(self, subject_kwargs=None, period_kwargs=None, assignment_kwargs=None,
                                assignment_group_kwargs=None, feedback_set_kwargs=None, with_group_comment=False,
                                group_comment_kwargs=None):
        subject = self.get_or_create_subject(subject_kwargs=subject_kwargs)
        period = self.get_or_create_period(subject=subject, period_kwargs=period_kwargs)
        assignment = self.get_or_create_assignment(period=period, assignment_kwargs=assignment_kwargs)
        assignment_group = self.get_or_create_assignment_group(
            assignment=assignment, assignment_group_kwargs=assignment_group_kwargs)
        feedback_set = self.get_or_create_feedback_set(assignment_group=assignment_group,
                                                       feedback_set_kwargs=feedback_set_kwargs)
        if with_group_comment:
            if not group_comment_kwargs:
                group_comment_kwargs = {}
            self.create_group_comment(feedback_set=feedback_set, group_comment_kwargs=group_comment_kwargs)

    def __create_for_migrate_db(self, subject_kwargs=None, period_kwargs=None, assignment_kwargs=None,
                                assignment_group_kwargs=None, feedback_set_kwargs=None, group_comment_kwargs=None):
        if not subject_kwargs:
            subject_kwargs = {'short_name': 'migrate_subject'}
        if not period_kwargs:
            period_kwargs = {'short_name': 'migrate_period'}
        if not assignment_kwargs:
            assignment_kwargs = {'short_name': 'migrate_assignment'}
        if not assignment_group_kwargs:
            assignment_group_kwargs = {'name': 'migrate_group'}
        subject = self.get_or_create_subject(subject_kwargs=subject_kwargs, db_alias=self.from_db_alias)
        period = self.get_or_create_period(subject=subject, period_kwargs=period_kwargs, db_alias=self.from_db_alias)
        assignment = self.get_or_create_assignment(period=period, assignment_kwargs=assignment_kwargs,
                                                   db_alias=self.from_db_alias)
        assignment_group = self.get_or_create_assignment_group(
            assignment=assignment, assignment_group_kwargs=assignment_group_kwargs, db_alias=self.from_db_alias)
        feedback_set = self.get_or_create_feedback_set(
            assignment_group=assignment_group, feedback_set_kwargs=feedback_set_kwargs, db_alias=self.from_db_alias)
        if not group_comment_kwargs:
            group_comment_kwargs = {}
        self.create_group_comment(
            feedback_set=feedback_set, group_comment_kwargs=group_comment_kwargs, db_alias=self.from_db_alias)

    def test_database_sanity(self):
        # Default database data
        self.__create_for_default_db(with_group_comment=True)

        # Migrate database data
        self.__create_for_migrate_db()

        # Test default database
        self.assertEqual(group_models.GroupComment.objects.count(), 1)
        self.assertEqual(group_models.GroupComment.objects.get().feedback_set.group.name, 'default_group')

        # Test migrate database
        self.assertEqual(group_models.GroupComment.objects.using(self.from_db_alias).count(), 1)
        self.assertEqual(
            group_models.GroupComment.objects.using(self.from_db_alias)
                .select_related('feedback_set', 'feedback_set__group').get().feedback_set.group.name, 'migrate_group')

    def test_feedback_set_not_imported_raises_exception(self):
        # Default database data
        self.__create_for_default_db(with_group_comment=True)

        # Migrate database data
        self.__create_for_migrate_db()

        # Create TempMergeId for Comment
        mommy.make('devilry_merge_v3database.TempMergeId',
                   from_id=comment_models.Comment.objects.using(self.from_db_alias).get().id,
                   to_id=comment_models.Comment.objects.get().id,
                   model_name='devilry_comment_comment')

        # Create TempMergeId for FeedbackSet
        mommy.make('devilry_merge_v3database.TempMergeId',
                   from_id=group_models.FeedbackSet.objects.using(self.from_db_alias).get().id,
                   to_id=group_models.FeedbackSet.objects.get().id,
                   model_name='devilry_group_feedbackset')

        with self.assertRaisesMessage(ValueError, 'FeedbackSets must be imported before GroupComments'):
            comment_merger.GroupCommentMerger(from_db_alias=self.from_db_alias, transaction=True).run()
