import random
import json

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils import lorem_ipsum
import traceback

from devilry.apps.core.models import StaticFeedback, Deadline
from devilry.apps.core.models import RelatedStudent
from devilry.apps.core.models import RelatedExaminer
from devilry.devilry_markup.parse_markdown import markdown_full
from devilry.project.develop.testhelpers.corebuilder import UserBuilder, NodeBuilder
from devilry.project.develop.testhelpers.datebuilder import DateTimeBuilder

bad_students = [
    ('dewey', 'Dewey Duck'),
    ('louie', 'Louie Duck'),
    ('huey', 'Huey Duck'),
    ('june', 'June Duck'),
    ('july', 'July Duck'),
    ('thor', 'God of Thunder'),
]

good_students = [
    ('baldr', 'God of Beauty'),
    ('freyja', 'Goddess of Love'),
    ('freyr', 'God of Fertility'),
    ('kvasir', 'God of Inspiration'),
    ('loki', 'Trickster and god of Mischief'),
    ('odin', 'The "All Father"')
]

programs = [
    {
        'filename': 'test.py',
        'data': 'print "Test"'
    },
    {
        'filename': 'hello.py',
        'data': 'if i == 10:\n    print "Hello"\nelse: pass'
    },
    {
        'filename': 'demo.py',
        'data': 'while True: pass'
    },
    {
        'filename': 'sum.py',
        'data': 'def sum(a, b):\n    return a+b\n'
    },
    {
        'filename': 'addtimes.py',
        'data': 'def addtimes(x, y, times=1):\n    return (x + y) * times\n'
    },
    {
        'filename': 'generate.py',
        'data': 'def generate(count):\n    return [randint(x, 100000) for x in xrange(count)]\n'
    },
    {
        'filename': 'count.py',
        'data': (
            'def count_true(iterable, attribute):\n'
            '    count = 0\n'
            '    for item in iterable:\n'
            '        if getattr(item, attribute):\n'
            '            count += 1\n'
            '    return count\n'
        )
    },
    {
        'filename': 'Hello.java',
        'data': (
            'class Hello {\n'
            '    public static void main(String [] args) {\n'
            '        System.out.println("Hello world");\n'
            '    }\n'
            '}')
    },
    {
        'filename': 'Demo.java',
        'data': (
            'class Demo {\n'
            '    public static void main(String [] args) {\n'
            '        System.out.println("Hello demo");\n'
            '        if(args[1].equals("add")) {\n'
            '            return;\n'
            '        }\n'
            '        else {\n'
            '            System.out.println("Else");\n'
            '        }\n'
            '    }\n'
            '}')
    },
]

comment_files = [
    {
        'filename': 'ObligNDelivery.py',
        'data': 'print "Test"',
        'filesize': 64,
    },
    {
        'filename': 'DesignDocumentForObligN.pdf',
        'data': 'Some text.',
        'filesize': 64,
    },
    {
        'filename': 'ObligN.py',
        'data': 'while True: pass',
        'filesize': 64,
    },
]

comment_texts = [
    u"Noooooo! Dr. Zoidberg, that doesn't make sense. But, okay! That's right, baby. I ain't your loverboy Flexo, the "
    u"guy you love so much. You even love anyone pretending to be him! Now that the, uh, garbage ball is in space, "
    u"Doctor, perhaps you can help me with my sexual inhibitions? No! The cat shelter's on to me. Eeeee! Now say "
    u"'nuclear wessels'!",
    u"But I know you in the future. I cleaned your poop. Say it in Russian! I don't know what you did, Fry, but once "
    u"again, you screwed up! Now all the planets are gonna start cracking wise about our mamas. Aww, it's true. I've "
    u"been hiding it for so long. Check it out, y'all. Everyone who was invited is here. Does anybody else feel "
    u"jealous and aroused and worried?",
    u"I had more, but you go ahead. Now Fry, it's been a few years since medical school, so remind me. Disemboweling "
    u"in your species: fatal or non-fatal? It's just like the story of the grasshopper and the octopus. All year long, "
    u"the grasshopper kept burying acorns for winter, while the octopus mooched off his girlfriend and watched TV. "
    u"But then the winter came, and the grasshopper died, and the octopus ate all his acorns. Also he got a race car. "
    u"Is any of this getting through to you? We're rescuing ya. I'm sorry, guys. I never meant to hurt you. Just to "
    u"destroy everything you ever believed in. Good news, everyone! There's a report on TV with some very bad news!",
    u"Is today's hectic lifestyle making you tense and impatient? And so we say goodbye to our beloved pet, Nibbler, "
    u"who's gone to a place where I, too, hope one day to go. The toilet. All I want is to be a monkey of moderate "
    u"intelligence who wears a suit... that's why I'm transferring to business school! Can we have Bender "
    u"Burgers again? Wow! A superpowers drug you can just rub onto your skin? You'd think it would be something you'd "
    u"have to freebase. Have you ever tried just turning off the TV, sitting down with your children, "
    u"and hitting them?",
    u"You lived before you met me?! For one beautiful night I knew what it was like to be a grandmother. Subjugated, "
    u"yet honored. Is today's hectic lifestyle making you tense and impatient? Good news, everyone! I've taught the "
    u"toaster to feel love! Bender, you risked your life to save me! Shut up and get to the point!",
    u"Maybe I love you so much I love you no matter who you are pretending to be. When I was first asked to make a "
    u"film about my nephew, Hubert Farnsworth, I thought 'Why should I?' Then later, Leela made the film. But if I "
    u"did make it, you can bet there would have been more topless women on motorcycles. Roll film! Oh right. "
    u"I forgot about the battle. THE BIG BRAIN AM WINNING AGAIN! I AM THE GREETEST! NOW I AM LEAVING EARTH, "
    u"FOR NO RAISEN!",
    u"Is today's hectic lifestyle making you tense and impatient? Hey! I'm a porno-dealing monster, what do "
    u"I care what you think? For the last time, I don't like lilacs! Your 'first' wife was the one who liked "
    u"lilacs! Really?! Ah, yes! John Quincy Adding Machine. He struck a chord with the voters when he pledged not to "
    u"go on a killing spree.",
    u"Alright, let's mafia things up a bit. Joey, burn down the ship. Clamps, burn down the crew. Maybe I love "
    u"you so much I love you no matter who you are pretending to be. Your best is an idiot! Well, thanks to the "
    u"Internet, I'm now bored with sex. Is there a place on the web that panders to my lust for violence?",
    u"Oh right. I forgot about the battle. And when we woke up, we had these bodies. Yep, I remember. They came "
    u"in last at the Olympics, then retired to promote alcoholic beverages!",
    u"Well, then good news! It's a suppository. Oh, how awful. Did he at least die painlessly? ...To shreds, you "
    u"say. Well, how is his wife holding up? ...To shreds, you say. And when we woke up, we had these bodies. "
    u"Actually, that's still true. And yet you haven't said what I told you to say! How can any of us trust you?",
    u"Nay, I respect and admire Harold Zoid too much to beat him to death with his own Oscar. I had more, but "
    u"you go ahead. Hey, whatcha watching?",
    u"So I really am important? How I feel when I'm drunk is correct? Check it out, y'all. Everyone who was invited "
    u"is here. I'm Santa Claus! Spare me your space age technobabble, Attila the Hun! So, how 'bout them Knicks?",
    u"No! The kind with looting and maybe starting a few fires! Why not indeed! Kids don't turn rotten just from "
    u"watching TV.",
    u"Meh. Say it in Russian! THE BIG BRAIN AM WINNING AGAIN! I AM THE GREETEST! NOW I AM LEAVING EARTH, "
    u"FOR NO RAISEN! Bender, being God isn't easy. If you do too much, people get dependent on you, and if "
    u"you do nothing, they lose hope. You have to use a light touch. Like a safecracker, or a pickpocket. Is "
    u"that a cooking show?",
    u"It's toe-tappingly tragic! Come, Comrade Bender! We must take to the streets! Hi, I'm a naughty nurse, "
    u"and I really need someone to talk to. $9.95 a minute. Bender, you risked your life to save me! I videotape "
    u"every customer that comes in here, so that I may blackmail them later. Actually, that's still true.",
    u"You guys aren't Santa! You're not even robots. How dare you lie in front of Jesus? Shut up and get to the "
    u"point! You're going back for the Countess, aren't you? Meh.",
    u"With a warning label this big, you know they gotta be fun! When I was first asked to make a film about my "
    u"nephew, Hubert Farnsworth, I thought 'Why should I?' Then later, Leela made the film. But if I did make it, "
    u"you can bet there would have been more topless women on motorcycles. Roll film! You are the last hope of the "
    u"universe. I suppose I could part with 'one' and still be feared... I wish! It's a nickel.",
    u"And yet you haven't said what I told you to say! How can any of us trust you? The key to victory is discipline, "
    u"and that means a well made bed. You will practice until you can make your bed in your sleep. There, now he's "
    u"trapped in a book I wrote: a crummy world of plot holes and spelling errors! Morbo can't understand his "
    u"teleprompter because he forgot how you say that letter that's shaped like a man wearing a hat.",
    u"Um, is this the boring, peaceful kind of taking to the streets? Man, I'm sore all over. I feel like I just "
    u"went ten rounds with mighty Thor. Bender! Ship! Stop bickering or I'm going to come back there and change "
    u"your opinions manually!",
    u"And so we say goodbye to our beloved pet, Nibbler, who's gone to a place where I, too, hope one day to go. "
    u"The toilet. Hey, you add a one and two zeros to that or we walk! But existing is basically all I do! "
    u"You can crush me but you can't crush my spirit!"
]


class Command(BaseCommand):
    help = 'Create a database for demo/testing.'

    def handle(self, *args, **options):
        self.grandma = UserBuilder('grandma',
                                   full_name='Elvira "Grandma" Coot',
                                   is_superuser=True).user
        self.thor = UserBuilder('thor',
                                full_name='God of Thunder and Battle').user
        self.donald = UserBuilder('donald',
                                  full_name='Donald Duck').user
        self.scrooge = UserBuilder('scrooge',
                                   full_name='Scrooge McDuck').user
        self.examiners = [self.donald, self.scrooge, self.thor]

        self.bad_students = {}
        for username, full_name in bad_students:
            self.bad_students[username] = self.create_or_get_user(username, full_name=full_name)
        self.good_students = {}
        for username, full_name in good_students:
            self.good_students[username] = self.create_or_get_user(username, full_name=full_name)
        self.allstudentslist = list(self.bad_students.values()) + list(list(self.good_students.values()))
        self.april = UserBuilder('april', full_name='April Duck').user

        for user in [self.thor, self.donald, self.april]:
            user.languagecode = 'nb'
            user.save()

        self.duckburgh = NodeBuilder('duckburgh', long_name="University of Duckburgh")
        self.add_emptycourse()
        self.add_duck1100()
        # self.add_hugecourse()
        self.create_feedbackset_complete()

    def create_or_get_user(self, username, full_name):
        try:
            return UserBuilder(username, full_name=full_name).user
        except ValidationError:
            if settings.DJANGO_CRADMIN_USE_EMAIL_AUTH_BACKEND:
                shortname = '{}@example.com'.format(username)
            else:
                shortname = username
            return get_user_model().objects.get(shortname=shortname)

    def build_random_pointassignmentdata(self,
                                         periodbuilder, weeks_ago, short_name, long_name,
                                         filecount,
                                         feedback_percent=100,
                                         bad_students=None, good_students=None):
        bad_students_iterator = bad_students or self.bad_students.itervalues()
        good_students_iterator = good_students or self.good_students.itervalues()

        assignmentbuilder = periodbuilder.add_assignment_x_weeks_ago(
            weeks=weeks_ago,
            short_name=short_name, long_name=long_name,
            passing_grade_min_points=1,
            grading_system_plugin_id='devilry_gradingsystemplugin_points',
            points_to_grade_mapper='raw-points',
            max_points=filecount,
            first_deadline=DateTimeBuilder.now().minus(weeks=weeks_ago - 1)
        )

        def create_group(user, minpoints, maxpoints, examiner):
            def create_old_delivery_structure():
                deadlinebuilder = groupbuilder \
                    .add_deadline(
                        deadline=Deadline.reduce_datetime_precision(
                            assignmentbuilder.assignment.first_deadline))

                deliverybuilder = deadlinebuilder.add_delivery_x_hours_before_deadline(
                    hours=random.randint(1, 30))
                used_filenames = set()
                for number in xrange(filecount):
                    while True:
                        deliveryfile = random.choice(programs)
                        filename = deliveryfile['filename']
                        if filename not in used_filenames:
                            used_filenames.add(filename)
                            break
                    deliverybuilder.add_filemeta(
                        filename=deliveryfile['filename'],
                        data=deliveryfile['data'])

                if random.randint(0, 100) <= feedback_percent:
                    feedback = StaticFeedback.from_points(
                        assignment=assignmentbuilder.assignment,
                        saved_by=examiner,
                        delivery=deliverybuilder.delivery,
                        rendered_view=self._lorem_paras(random.randint(1, 5)),
                        points=random.randint(minpoints, maxpoints))
                    feedback.save()

            def create_feedbackset_structure():

                def randomize_files():
                    return random.sample(comment_files, int(random.uniform(0, len(comment_files))))

                def get_comment_text():
                    return comment_texts[int(random.uniform(0, len(comment_texts)))]

                feedbacksetbuilder = groupbuilder.add_feedback_set(
                    points=random.randint(minpoints, maxpoints),
                    published_by=examiner,
                    created_by=examiner,
                    deadline_datetime=DateTimeBuilder.now().minus(weeks=weeks_ago),
                    gradeform_json="test"
                )

                # add student delivery
                feedbacksetbuilder.add_groupcomment(
                    files=randomize_files(),
                    user=user,
                    user_role="student",
                    instant_publish=True,
                    visible_for_students=True,
                    text=get_comment_text(),
                    published_datetime=DateTimeBuilder.now().minus(weeks=weeks_ago, days=4))

                users = [{'user': user, 'role': 'student'}, {'user': examiner, 'role': 'examiner'}]
                # add random comments
                for i in xrange(0, int(random.uniform(0, 5))):
                    random_user = users[int(random.uniform(0, 1))]
                    feedbacksetbuilder.add_groupcomment(
                        files=randomize_files(),
                        user=random_user['user'],
                        user_role=random_user['role'],
                        instant_publish=True,
                        visible_for_students=True,
                        text=get_comment_text(),
                        published_datetime=DateTimeBuilder.now().minus(weeks=weeks_ago, days=3,
                                                                       hours=int(random.uniform(0, 23))))

                # add examiner feedback
                feedbacksetbuilder.add_groupcomment(
                    files=randomize_files(),
                    user=examiner,
                    user_role="examiner",
                    instant_publish=bool(random.getrandbits(1)),
                    visible_for_students=True,
                    text=get_comment_text(),
                    published_datetime=DateTimeBuilder.now().minus(weeks=weeks_ago, days=2))

            try:
                relatedstudent = RelatedStudent.objects.get(period=assignmentbuilder.assignment.period,
                                                            user=user)
            except:
                print()
                print("*" * 70)
                print()
                print(user)
                print()
                print("*" * 70)
                print()

                raise
            groupbuilder = assignmentbuilder.add_group(
                relatedstudents=[relatedstudent], examiners=[examiner])

            if weeks_ago > 52:
                create_old_delivery_structure()
            else:
                create_feedbackset_structure()

        for user in bad_students_iterator:
            create_group(user, minpoints=0, maxpoints=filecount / 2,
                         examiner=random.choice(self.examiners))
        for user in good_students_iterator:
            create_group(user, minpoints=filecount / 2, maxpoints=filecount,
                         examiner=random.choice(self.examiners))
        create_group(self.april, minpoints=1, maxpoints=filecount,
                     examiner=self.donald)
        return assignmentbuilder

    def _as_relatedstudents(self, users, tags):
        return [RelatedStudent(user=user, tags=tags) for user in users]

    def add_emptycourse(self):
        democourse = self.duckburgh.add_subject(
            short_name='democourse',
            long_name='DEMO101 - A demo course')
        democourse.add_admins(self.thor)
        print
        print("*" * 70)
        print
        print('Empty course named "DEMO101 - A demo course" added')
        print
        print("*" * 70)
        print

    def add_hugecourse(self):
        duck1100 = self.duckburgh.add_subject(
            short_name='hugecourse',
            long_name='HUGE1000 - A huge testcourse')
        duck1100.add_admins(self.thor)

        periodbuilder = duck1100.add_6month_active_period(
            short_name='testsemester', long_name='Testsemester',
            relatedexaminers=[
                RelatedExaminer(user=self.thor, tags=''),
                RelatedExaminer(user=self.donald, tags='group1'),
                RelatedExaminer(user=self.scrooge, tags='group2')
            ])

        bad_studentusers = []
        good_studentusers = []
        relatedstudents = []
        for x in xrange(2000):
            studentuser = UserBuilder('student{}'.format(x)).user
            if random.randint(0, 1):
                good_studentusers.append(studentuser)
            else:
                bad_studentusers.append(studentuser)
            relatedstudent = RelatedStudent(
                period=periodbuilder.period,
                user=studentuser,
                tags='group{}'.format(random.randint(1, 2)))
            relatedstudents.append(relatedstudent)
        RelatedStudent.objects.bulk_create(relatedstudents)

        self.build_random_pointassignmentdata(
            periodbuilder=periodbuilder,
            weeks_ago=2, filecount=2,
            short_name='oblig1', long_name='Obligatory assignment one',
            bad_students=bad_studentusers,
            good_students=good_studentusers)

    def add_duck1100(self):
        duck1100 = self.duckburgh.add_subject(
            short_name='duck1100',
            long_name='DUCK1100 - Programming for the natural sciences')
        duck1100.add_admins(self.thor)

        relatedstudents = [
            RelatedStudent(user=self.april, tags='group1'),
        ]
        relatedstudents.extend(self._as_relatedstudents(self.good_students.values(), 'group1'))
        relatedstudents.extend(self._as_relatedstudents(self.bad_students.values(), 'group2'))
        testsemester = duck1100.add_6month_active_period(
            short_name='testsemester', long_name='Testsemester',
            relatedstudents=relatedstudents,
            relatedexaminers=[
                RelatedExaminer(user=self.thor, tags=''),
                RelatedExaminer(user=self.donald, tags='group1'),
                RelatedExaminer(user=self.scrooge, tags='group2')
            ])

        # old_relatedstudentusers = [
        #     self.thor,
        #     self.april, self.bad_students['dewey'],
        #     self.bad_students['louie'], self.bad_students['june'],
        #     self.good_students['loki'], self.good_students['kvasir']]
        # old_relatedstudents = self._as_relatedstudents(old_relatedstudentusers, tags='')
        oldtestsemester = duck1100.add_6month_lastyear_period(
            short_name='oldtestsemester', long_name='Old testsemester',
            relatedstudents=relatedstudents,
            relatedexaminers=[
                RelatedExaminer(user=self.thor, tags=''),
                RelatedExaminer(user=self.donald, tags='group1'),
                RelatedExaminer(user=self.scrooge, tags='group2')
            ])

        for periodbuilder, weekoffset in [
                (oldtestsemester, 52),
                (testsemester, 0)]:
            self.build_random_pointassignmentdata(
                periodbuilder=periodbuilder,
                weeks_ago=weekoffset + 6, filecount=4,
                short_name='week1', long_name='Week 1')
            self.build_random_pointassignmentdata(
                periodbuilder=periodbuilder,
                weeks_ago=weekoffset + 5, filecount=2,
                short_name='week2', long_name='Week 2')
            self.build_random_pointassignmentdata(
                periodbuilder=periodbuilder,
                weeks_ago=weekoffset + 4, filecount=4,
                short_name='week3', long_name='Week 3')
            self.build_random_pointassignmentdata(
                periodbuilder=periodbuilder,
                weeks_ago=weekoffset + 3, filecount=8,
                short_name='week4', long_name='Week 4')

            if weekoffset == 0:
                self.build_random_pointassignmentdata(
                    periodbuilder=periodbuilder,
                    weeks_ago=weekoffset + 1, filecount=6,
                    short_name='week5', long_name='Week 5',
                    feedback_percent=50)

                week6 = periodbuilder.add_assignment_x_weeks_ago(
                    weeks=weekoffset, short_name='week6', long_name='Week 6',
                    passing_grade_min_points=1,
                    grading_system_plugin_id='devilry_gradingsystemplugin_points',
                    points_to_grade_mapper='raw-points',
                    max_points=6
                )
                for user in self.allstudentslist + [self.april]:
                    examiner = random.choice(self.examiners)
                    week6 \
                        .add_group(students=[user], examiners=[examiner]) \
                        .add_deadline(deadline=Deadline.reduce_datetime_precision(DateTimeBuilder.now().plus(days=7)))
            else:
                self.build_random_pointassignmentdata(
                    periodbuilder=periodbuilder,
                    weeks_ago=weekoffset + 1, filecount=1,
                    short_name='week5', long_name='Week 5')
                self.build_random_pointassignmentdata(
                    periodbuilder=periodbuilder,
                    weeks_ago=weekoffset, filecount=2,
                    short_name='week6', long_name='Week 6')

        print
        print("*" * 70)
        print
        print('duck1100 added')
        print
        print("*" * 70)
        print

    def create_feedbackset_complete(self):
        # Create a finished feedback_set for a specified user on a new subject
        # and a new assingment in the current period
        student = UserBuilder('psylocke', full_name='Elisabeth Braddock').user
        examiner = UserBuilder('magneto', full_name='Erik Lehnsherr').user
        examiner2 = UserBuilder('beast', full_name='Hank McCoy').user

        first_deadline = timezone.now() - timezone.timedelta(weeks=2, days=1)


        assignment_setup_gradeform_json = {
            "type": "advanced",
            "id": "uyagsfuyg43t763t42gtysfeg82376rf2uytf27836dgfweytfgv7238",
            "schema":
            [

                {
                  "id": "uasgf87###ASDSAIDQuestion title",
                  "title":"Question title",
                  "explanation":"Explanation of how to fill in",
                  "options_type":"range",
                  "range_from": 0,
                  "range_to": 100,
                  "value": 50,
                  "comment": ""
                },

                {
                  "id": "uasek32002AIDQuestion title",
                  "title":"Question title",
                  "explanation":"Explanation of how to fill in",
                  "options_type":"single_select",
                  "options":
                  [
                    {"value": "false", "points": 1, "choise_text":"some choise", "comment": ""},
                    {"value": "false", "points": 1, "choise_text":"some choise", "comment": ""},
                    {"value": "false", "points": 1, "choise_text":"some choise", "comment": ""},
                    {"value": "false", "points": 1, "choise_text":"some choise", "comment": ""}
                  ]
                },

                {
                  "id": "ullsoqppp987#@asdIDQuestion title",
                  "title":"Question title",
                  "explanation":"Explanation of how to fill in",
                  "options_type":"multi_select",
                  "options":
                  [
                    {"value": "false", "points": 1, "choise_text":"some choise", "comment": ""},
                    {"value": "false", "points": 1, "choise_text":"some choise", "comment": ""},
                    {"value": "false", "points": 1, "choise_text":"some choise", "comment": ""},
                    {"value": "false", "points": 1, "choise_text":"some choise", "comment": ""}
                  ]
                },

                {
                  "id": "sdaikjfoa4788698236487263847iwufghQuestion title",
                  "title":"Question title",
                  "explanation":"Explanation of how to fill in",
                  "options_type":"feedback",
                  "feedback": "some written feedback in a textarea"
                }
            ]
        }

        data = {
            'type': 'advanced',
            'scheme': [
                {"points_max": "5", "points_achieved": "5", "text": "Has the student documented the code?", "comment": "Great documentation"},
                {"points_max": "5", "points_achieved": "3", "text": "Implemented own datastructures?", "comment": "You where meant to implement all datastructures. You didn't implement the hashmap ='("},
                {"points_max": "5", "points_achieved": "4", "text": "Has the student understood the different pros and cons for the datastructures?", "comment": "Shows good understanding"},
                {"points_max": "5", "points_achieved": "0", "text": "Fullfilling designdocument?", "comment": "You where supposed to deliver a document with CONTENT, not an empty one!"},
            ]
        }

        periodbuilder = self.duckburgh.add_subject(
            short_name='inf7020',
            long_name='INF7020 Programming for World Domination and Crashing Non-Mutant Economy',
        ).add_6month_active_period(
            short_name='testsemester',
            long_name='Testsemester',
            relatedexaminers=[
                RelatedExaminer(user=examiner),
                RelatedExaminer(user=examiner2),
            ],
            relatedstudents=[student])
        assignmentgroupbuilder = periodbuilder.add_assignment(
            'Oblig 1 - Domination',
            passing_grade_min_points=3,
            max_points=10,
            first_deadline=first_deadline,
            gradeform_setup_json=json.dumps(assignment_setup_gradeform_json)
        ).add_group()

        assignmentgroupbuilder.add_candidates_from_relatedstudents(
            *periodbuilder.period.relatedstudent_set.all())
        assignmentgroupbuilder.add_examiners(examiner, examiner2)

        feedbacksetbuilder1 = assignmentgroupbuilder.add_feedback_set(
            points=1,
            published_by=examiner,
            created_by=examiner,
            published_datetime=DateTimeBuilder.now().minus(weeks=1, days=5, hours=2),
            created_datetime=DateTimeBuilder.now().minus(weeks=4),
            deadline_datetime=first_deadline,
            gradeform_json=json.dumps(data)
        )

        # Event summary for feedback_set 1
        feedbacksetbuilder1.add_groupcomment(
            user=student,
            user_role='student',
            instant_publish=True,
            visible_for_students=True,
            text="I don't know how to solve this, can't I just use my private army?",
            published_datetime=DateTimeBuilder.now().minus(weeks=2, days=2)
        )

        feedbacksetbuilder1.add_groupcomment(
            user=examiner,
            user_role='examiner',
            instant_publish=True,
            visible_for_students=True,
            text="No no no, you're here to learn how to get domination using information "
                 "technology. Later you will learn to use automate your abilities by programming them.",
            published_datetime=DateTimeBuilder.now().minus(weeks=2, days=2)
        )

        feedbacksetbuilder1.add_groupcomment(
            files=[comment_files[0]],
            user=student,
            user_role='student',
            instant_publish=True,
            visible_for_students=True,
            text='Here my assignment! I think I have a great solution! =D',
            published_datetime=DateTimeBuilder.now().minus(weeks=2, days=1, hours=1)
        )

        feedbacksetbuilder1.add_groupcomment(
            files=[comment_files[1]],
            user=student,
            user_role='student',
            instant_publish=True,
            visible_for_students=True,
            text='Wuups! Forgot this file!',
            published_datetime=DateTimeBuilder.now().minus(weeks=1, days=5, hours=3)
        )

        feedbacksetbuilder1.add_groupcomment(
            files=[comment_files[1]],
            user=examiner,
            user_role='examiner',
            instant_publish=True,
            visible_for_students=True,
            text="You failed miserably! Try to actually understand the problem. Printing 'hello world, I own you now' "
                 "everywhere won't get you anywhere!",
            published_datetime=feedbacksetbuilder1.feedback_set.published_datetime
            # DateTimeBuilder.now().minus(weeks=1, days=5, hours=1)
        )

        feedbacksetbuilder1.add_groupcomment(
            user=student,
            user_role='student',
            instant_publish=True,
            visible_for_students=True,
            text='Noooooooo! New try pls?',
            published_datetime=DateTimeBuilder.now().minus(weeks=1, days=4, hours=23)
        )

        feedbacksetbuilder1.add_groupcomment(
            user=examiner,
            user_role='examiner',
            instant_publish=True,
            visible_for_students=True,
            text="Ok, I'll give you a second try!",
            published_datetime=DateTimeBuilder.now().minus(weeks=1, days=4, hours=22)
        )


        # Event summary for feedback_set 2
        feedbacksetbuilder2 = assignmentgroupbuilder.add_feedback_set(
            points=10,
            published_by=examiner,
            created_by=examiner,
            published_datetime=DateTimeBuilder.now().minus(weeks=0, days=3),
            created_datetime=DateTimeBuilder.now().minus(weeks=1, days=4, hours=21),
            deadline_datetime=DateTimeBuilder.now().minus(weeks=1),
            gradeform_json=json.dumps(data)
        )

        feedbacksetbuilder2.add_groupcomment(
            user=student,
            user_role='student',
            instant_publish=True,
            visible_for_students=True,
            text="Thanks!",
            published_datetime=DateTimeBuilder.now().minus(weeks=1, days=4, hours=18)
        )

        feedbacksetbuilder2.add_groupcomment(
            user=student,
            user_role='student',
            instant_publish=True,
            visible_for_students=True,
            text="Do you like cashew nuts?",
            published_datetime=DateTimeBuilder.now().minus(weeks=1, days=4, hours=16)
        )

        feedbacksetbuilder2.add_groupcomment(
            user=examiner,
            user_role='examiner',
            instant_publish=True,
            visible_for_students=True,
            text="Stay on topic please... But, yes...",
            published_datetime=DateTimeBuilder.now().minus(weeks=1, days=3)
        )

        feedbacksetbuilder2.add_groupcomment(
            files=[comment_files[0], comment_files[1]],
            user=student,
            user_role='student',
            instant_publish=True,
            visible_for_students=True,
            text='Here we go again!',
            published_datetime=DateTimeBuilder.now().minus(weeks=1, days=2)
        )

        feedbacksetbuilder2.add_groupcomment(
            files=[comment_files[2]],
            user=examiner,
            user_role='examiner',
            instant_publish=True,
            visible_for_students=True,
            text="Great job! You must be the most evil mutant I have ever met! Keep going like this, "
                 "and you'll own the entire planet in no time!",
            published_datetime=feedbacksetbuilder2.feedback_set.published_datetime
            # DateTimeBuilder.now().minus(weeks=0, days=3)
        )

        feedbacksetbuilder2.add_groupcomment(
            user=student,
            user_role='student',
            instant_publish=True,
            visible_for_students=True,
            text="Thanks! Sorry for the first delivery, I was so hungover when I worked on that!",
            published_datetime=DateTimeBuilder.now().minus(weeks=0, days=2)
        )

    def _lorem_paras(self, count):
        return markdown_full(u'\n\n'.join(
            lorem_ipsum.paragraphs(count, common=False))
        )
