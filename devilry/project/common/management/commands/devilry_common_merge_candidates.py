from django.core.management.base import BaseCommand, CommandError
from django.contrib import auth
from django.db import IntegrityError
from django.db import transaction
from django.core.exceptions import ValidationError

from optparse import make_option

from devilry.apps.core.models import candidate


class Command(BaseCommand):
    help = 'Merge two users by altering the student attribute on all candidates from the first user to the second.' \
           'All migrations will happen in a single transaction, and be rolled back in case of ' \
           'IntegrityError or ValidationError'

    args = '<old user> <new user>'

    option_list = BaseCommand.option_list + (

        make_option(
            '--test',
            action='store_true',
            default=False,
            dest='test',
            help='simply display what will be migrated, with no actual database alterations.'),

        make_option(
            '--display_migrations',
            action='store_true',
            default=False,
            dest='display_migrations',
            help='print all migrations once they occur.'),

        make_option(
            '--use_email',
            action='store_true',
            default=False,
            dest='use_email',
            help='identify users by email. If this flag is set, the --use_pk flag will be ignored'),

        make_option(
            '--use_username',
            action='store_true',
            default=False,
            dest='use_username',
            help='identify users by username. If this flag is set, the --use_pk flag will be ignored'),

        make_option(
            '--use_pk',
            action='store_true',
            default=True,
            dest='use_pk',
            help='identify users by pk. On by default.'))


    def __get_users(self, *args, **options):
        user_model = auth.get_user_model()
        if options['use_email']:
            try:
                old_user = user_model.objects.get(email=args[0])
            except user_model.DoesNotExist:
                raise CommandError("Could not find user with email {}".format(args[0]))
            try:
                new_user = user_model.objects.get(email=args[1])
            except user_model.DoesNotExist:
                raise CommandError("Could not find user with email {}".format(args[1]))
        elif options['use_username']:
            try:
                old_user = user_model.objects.get(username=args[0])
            except user_model.DoesNotExist:
                raise CommandError("Could not find user with username {}".format(args[0]))
            try:
                new_user = user_model.objects.get(username=args[1])
            except user_model.DoesNotExist:
                raise CommandError("Could not find user with username {}".format(args[1]))
        elif options['use_pk']:
            try:
                old_user = user_model.objects.get(pk=args[0])
            except user_model.DoesNotExist:
                raise CommandError("Could not find user with pk {}".format(args[0]))
            try:
                new_user = user_model.objects.get(pk=args[1])
            except user_model.DoesNotExist:
                raise CommandError("Could not find user with pk {}".format(args[1]))
        else:
            raise CommandError("No email, and no pk? Something is very wrong - please check my source code!")

        return old_user, new_user

    def handle(self, *args, **options):
        if not len(args) == 2:
            raise CommandError("Need at least to user-identifiers to merge candidates")

        if not options['use_email'] and not options['use_pk'] and not options['use_username']:
            raise CommandError("Either --use_pk, --use_username or --use_email must be set")

        if options['use_email'] and options['use_username']:
            raise CommandError("Cannot use both username and email!")

        old_user, new_user = self.__get_users(*args, **options)

        old_candidates = candidate.Candidate.objects.filter(student=old_user)

        if options['test']:
            print 'Migrations:'
            for migrate_candidate in old_candidates:
                print '{}'.format(migrate_candidate)
        else:
            with transaction.atomic():
                for migrate_candidate in old_candidates:
                    migrate_candidate.student = new_user
                    try:
                        migrate_candidate.full_clean()
                        migrate_candidate.save()
                    except IntegrityError:
                        transaction.rollback()
                        CommandError("IntegrityError occurred while migrating:\n\t{}", migrate_candidate)
                    except ValidationError:
                        transaction.rollback()
                        CommandError("ValidationError occurred while migrating:\n\t{}", migrate_candidate)
                    else:
                        if options['display_migrations']:
                            print 'migrated: {}'.format(migrate_candidate)
