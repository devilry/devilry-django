from devilry.devilry_superadmin.management.commands.devilry_periodsetrelatedexaminers import RelatedBaseCommand


class Command(RelatedBaseCommand):
    help = 'Set related students on a period. Users are read from stdin, as a JSON encoded array of arguments to the RelatedStudent model. See devilry/apps/superadmin/examples/relatedstudents.json for an example.'
    user_type = "student"

    def handle(self, *args, **options):
        from devilry.apps.core.models import RelatedStudent
        self.get_subject_and_period(args)
        self.add_users(RelatedStudent, args, options)
