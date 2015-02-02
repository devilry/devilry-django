from devilry.project.develop.testhelpers.corebuilder import UserBuilder


class DemoUser(object):
    def __init__(self, username, full_name,
                 is_student=False,
                 studenttype=None,
                 is_examiner=False,
                 is_periodadmin=False,
                 is_courseadmin=False,
                 is_subjectadmin=False,
                 is_nodeadmin=False,
                 is_superuser=False):
        self.username = username
        self.full_name = full_name
        self.studenttype = studenttype
        self.is_examiner = is_examiner
        self.is_periodadmin = is_periodadmin
        self.is_courseadmin = is_courseadmin
        self.is_subjectadmin = is_subjectadmin
        self.is_nodeadmin = is_nodeadmin
        self.is_superuser = is_superuser

    def create_user(self):
        return UserBuilder(self.username, full_name=self.full_name, is_superuser=self.is_superuser).user


class Users(object):
    ###################################
    #
    # Users used by the demodb:
    #
    # - Bad students are children from the duckburgh universe.
    # - Good students are northern gods.
    # - Examiners are superheroes.
    # - Node admins are transformers characters.
    # - Course admins are female simpsons characters.
    # - Period admins are male simpsons characters.
    # - Multipurpose users are characters from Futurama.
    #
    ###################################
    demousers = [

        # Bad students
        DemoUser(
            username='dewey',
            full_name='Dewey Duck',
            is_student=True,
            studenttype='bad'
        ),
        DemoUser(
            username='louie',
            full_name='Louie Duck',
            is_student=True,
            studenttype='bad'
        ),
        DemoUser(
            username='huey',
            full_name='Huey Duck',
            is_student=True,
            studenttype='bad'
        ),
        DemoUser(
            username='june',
            full_name='June Duck',
            is_student=True,
            studenttype='bad'
        ),
        DemoUser(
            username='july',
            full_name='July Duck',
            is_student=True,
            studenttype='bad'
        ),
        DemoUser(
            username='april',
            full_name='April Duck',
            is_student=True,
            studenttype='bad'
        ),

        # Good students
        DemoUser(
            username='baldr',
            full_name='God of Beauty',
            is_student=True,
            studenttype='good'
        ),
        DemoUser(
            username='freyja',
            full_name='Goddess of Love',
            is_student=True,
            studenttype='good'
        ),
        DemoUser(
            username='freyr',
            full_name='God of Fertility',
            is_student=True,
            studenttype='good'
        ),
        DemoUser(
            username='kvasir',
            full_name='God of Inspiration',
            is_student=True,
            studenttype='good'
        ),
        DemoUser(
            username='loki',
            full_name='Trickster and god of Mischief',
            is_student=True,
            studenttype='good'
        ),
        DemoUser(
            username='odin',
            full_name='The "All Father"',
            is_student=True,
            studenttype='good'
        ),
        DemoUser(
            username='thor',
            full_name='God of Thunder and Battle',
            is_student=True,
            studenttype='good'
        ),

        # Examiners
        DemoUser(
            username='spiderman',
            full_name='Peter Parker',
            is_examiner=True
        ),
        DemoUser(
            username='superman',
            full_name='Clark Kent',
            is_examiner=True
        ),

        # Period admins
        DemoUser(
            username='homer',
            full_name='Homer Simpson',
            is_periodadmin=True
        ),

        # Course admins
        DemoUser(
            username='marge',
            full_name='Marge Simpson',
            is_periodadmin=True
        ),

        # Node admins
        DemoUser(
            username='optimus',
            full_name='Optimus Prime',
            is_periodadmin=True
        ),


        # Superusers
        DemoUser(
            username='grandma',
            full_name='Elvira "Grandma" Coot',
            is_superuser=True
        ),

        # Multipurpose users
        # - These have multiple roles, and are typically used during development
        # - Only professor is superuser!
        DemoUser(
            username='bender',
            full_name='Bender',
            is_student=True,
            studenttype='good',
            is_examiner=True,
            is_nodeadmin=True,
            is_courseadmin=True,
        ),
        DemoUser(
            username='fry',
            full_name='Phillip J. Fry',
            is_student=True,
            studenttype='bad',
            is_examiner=True,
            is_nodeadmin=True,
            is_courseadmin=True,
        ),
        DemoUser(
            username='leela',
            full_name='Leela',
            is_student=True,
            studenttype='good',
            is_examiner=True,
            is_courseadmin=True,
            is_superuser=True,
        ),
        DemoUser(
            username='professor',
            full_name='Professor Hubert J. Farnsworth',
            is_student=True,
            studenttype='bad',
            is_examiner=True,
            is_superuser=True,
            is_courseadmin=True,
        )
    ]

    def create_all_users(self):
        for demouser in self.demousers:
            demouser.create_user()
