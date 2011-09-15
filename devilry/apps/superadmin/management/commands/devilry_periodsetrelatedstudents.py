from devilry_periodsetrelatedexaminers import RelatedBaseCommand


class Command(RelatedBaseCommand):
    help = 'Set related students on a period. Usernames are read from stdin, one username on each line.'
    user_type = "student"

    def handle(self, *args, **options):
        self.get_course_and_period(args)
        self.add_users(self.period.relatedstudents, args, options)
