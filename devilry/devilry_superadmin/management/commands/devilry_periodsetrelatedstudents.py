from devilry.devilry_superadmin.management.commands.devilry_periodsetrelatedexaminers import RelatedBaseCommand


class Command(RelatedBaseCommand):
    help = 'Set related students on a period. Users are read from stdin, as ' \
           'a JSON encoded array of arguments to the RelatedStudent model. ' \
           'See devilry/apps/superadmin/examples/relatedstudents.json for ' \
           'an example.'

    @property
    def user_type(self):
        return "student"

    @property
    def related_user_model_class(self):
        from devilry.apps.core.models import RelatedStudent
        return RelatedStudent

    def handle(self, *args, **options):
        super(Command, self).handle(*args, **options)
        self.get_subject_and_period()
        self.add_users()
