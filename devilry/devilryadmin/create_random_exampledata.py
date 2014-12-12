import json
import logging
import itertools
from random import randint
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.db.utils import IntegrityError

from devilry.apps.core.models import Delivery
from devilry.apps.core import pluginloader

pluginloader.autodiscover()



FEEDBACK_TEMPLATES = [
"""
<p><b>Michael Joseph Jackson</b><sup id="cite_ref-Legal_name_0-1" class="reference"><a href="#cite_note-Legal_name-0"><span>[</span>1<span>]</span></a></sup> (August 29, 1958 - June 25, 2009) was an American recording artist, dancer, singer-songwriter, musician, and philanthropist. Referred to as the <a href="/wiki/Honorific_nicknames_in_popular_music" title="Honorific nicknames in popular music">King of Pop</a>, Jackson is recognized as the most successful entertainer of all time by <a href="/wiki/Guinness_World_Records" title="Guinness World Records">Guinness World Records</a>. His contribution to music, dance, and fashion, along with a much-publicized personal life, made him a global figure in <a href="/wiki/Popular_culture" title="Popular culture">popular culture</a> for over four decades. The seventh child of the <a href="/wiki/Jackson_family" title="Jackson family">Jackson family</a>, he debuted on the professional music scene along with his brothers as a member of <a href="/wiki/The_Jackson_5" title="The Jackson 5">The Jackson 5</a>, then the Jacksons in 1964, and began his solo career in 1971.</p> 
<p>In the early 1980s, Jackson became a dominant figure in <a href="/wiki/Popular_music" title="Popular music">popular music</a>. The music videos for his songs, including those of "<a href="/wiki/Beat_It" title="Beat It">Beat It</a>", "<a href="/wiki/Billie_Jean" title="Billie Jean">Billie Jean</a>", and "<a href="/wiki/Thriller_(song)" title="Thriller (song)">Thriller</a>", were credited with transforming the medium into an art form and a promotional tool, and the popularity of these videos helped to bring the relatively new television channel MTV to fame. Videos such as "<a href="/wiki/Black_or_White" title="Black or White">Black or White</a>" and "<a href="/wiki/Scream/Childhood" title="Scream/Childhood">Scream</a>" made him a staple on MTV in the 1990s. Through stage performances and music videos, Jackson popularized a number of dance techniques, such as the <a href="/wiki/Robot_(dance)" title="Robot (dance)">robot</a> and the <a href="/wiki/Moonwalk_(dance)" title="Moonwalk (dance)">moonwalk</a>, to which he gave the name. His distinctive musical sound and vocal style have influenced numerous <a href="/wiki/Hip_hop_music" title="Hip hop music">hip hop</a>, pop, <a href="/wiki/Contemporary_R%26B" title="Contemporary R&amp;B">contemporary R&amp;B</a>, and rock artists.</p> 

<h2>Life and career</h2>
<h3>Early life and The Jackson 5 (1958-1975)</h3>
<p>Michael Jackson was born on August 29, 1958, the eighth of ten children in an African American working-class family who lived in a small 3-room house in <a href="/wiki/Gary,_Indiana" title="Gary, Indiana">Gary</a>, Indiana,<sup id="cite_ref-2" class="reference"><a href="#cite_note-2"><span>[</span>3<span>]</span></a></sup> an industrial suburb of Chicago. His mother, <a href="/wiki/Katherine_Jackson" title="Katherine Jackson">Katherine Esther Scruse</a>, was a devout <a href="/wiki/Jehovah%27s_Witness" title="Jehovah's Witness" class="mw-redirect">Jehovah's Witness</a>, and his father, <a href="/wiki/Joe_Jackson_(manager)" title="Joe Jackson (manager)">Joseph Walter "Joe" Jackson</a>, was a steel mill worker who performed with an R&amp;B band called The Falcons. Jackson had three sisters: <a href="/wiki/Rebbie_Jackson" title="Rebbie Jackson">Rebbie</a>, <a href="/wiki/La_Toya_Jackson" title="La Toya Jackson">La Toya</a>, and <a href="/wiki/Janet_Jackson" title="Janet Jackson">Janet</a>, and five brothers: <a href="/wiki/Jackie_Jackson" title="Jackie Jackson">Jackie</a>, <a href="/wiki/Tito_Jackson" title="Tito Jackson">Tito</a>, <a href="/wiki/Jermaine_Jackson" title="Jermaine Jackson">Jermaine</a>, <a href="/wiki/Marlon_Jackson" title="Marlon Jackson">Marlon</a>, and <a href="/wiki/Randy_Jackson_(The_Jacksons)" title="Randy Jackson (The Jacksons)">Randy</a>.<sup id="cite_ref-Nelson_George_overview_20_3-0" class="reference"><a href="#cite_note-Nelson_George_overview_20-3"><span>[</span>4<span>]</span></a></sup> A sixth brother, Brandon, died shortly after birth.<sup id="cite_ref-4" class="reference"><a href="#cite_note-4"><span>[</span>5<span>]</span></a></sup></p>

<h3>Move to Epic and <i>Off the Wall</i> (1975-81)</h3> 
<p>In June 1975, the Jackson 5 signed with <a href="/wiki/Epic_Records" title="Epic Records">Epic Records</a>, a subsidiary of <a href="/wiki/Sony_Music_Entertainment" title="Sony Music Entertainment">CBS Records</a><sup id="cite_ref-Nelson_George_overview_22_15-1" class="reference"><a href="#cite_note-Nelson_George_overview_22-15"><span>[</span>16<span>]</span></a></sup> and renamed themselves the Jacksons. Younger brother Randy formally joined the band around this time, while Jermaine left to pursue a solo career.<sup id="cite_ref-tara_138.E2.80.93144_16-0" class="reference"><a href="#cite_note-tara_138.E2.80.93144-16"><span>[</span>17<span>]</span></a></sup> They continued to tour internationally, releasing six more albums between 1976 and 1984, during which Michael was the lead songwriter, writing hits such as "<a href="/wiki/Shake_Your_Body_(Down_to_the_Ground)" title="Shake Your Body (Down to the Ground)">Shake Your Body (Down to the Ground)</a>", "<a href="/wiki/This_Place_Hotel" title="This Place Hotel">This Place Hotel</a>," and "<a href="/wiki/Can_You_Feel_It" title="Can You Feel It">Can You Feel It</a>".<sup id="cite_ref-RRHF_13-1" class="reference"><a href="#cite_note-RRHF-13"><span>[</span>14<span>]</span></a></sup> In 1978, he starred as the <a href="/wiki/Scarecrow_(Oz)" title="Scarecrow (Oz)">scarecrow</a> in the musical, <i><a href="/wiki/The_Wiz_(film)" title="The Wiz (film)">The Wiz</a></i>, a box-office disaster. It was here that he teamed up with <a href="/wiki/Quincy_Jones" title="Quincy Jones">Quincy Jones</a>, who was arranging the film's musical score. Jones agreed to produce Jackson's next solo album, <i><a href="/wiki/Off_the_Wall_(album)" title="Off the Wall (album)">Off the Wall</a></i>.<sup id="cite_ref-Nelson_George_overview_23_17-0" class="reference"><a href="#cite_note-Nelson_George_overview_23-17"><span>[</span>18<span>]</span></a></sup> In 1979, Jackson broke his nose during a complex dance routine. His subsequent <a href="/wiki/Rhinoplasty" title="Rhinoplasty">rhinoplasty</a> was not a complete success; he complained of breathing difficulties that would affect his career. He was referred to Dr. <a href="/wiki/Steven_Hoefflin" title="Steven Hoefflin">Steven Hoefflin</a>, who performed Jackson's second rhinoplasty and subsequent operations.<sup id="cite_ref-tara_205.E2.80.93210_18-0" class="reference"><a href="#cite_note-tara_205.E2.80.93210-18"><span>[</span>19<span>]</span></a></sup></p> 
<p>Jones and Jackson produced the <i>Off the Wall</i> album together. Songwriters for the album included Jackson, <a href="/wiki/Rod_Temperton" title="Rod Temperton">Rod Temperton</a>, <a href="/wiki/Stevie_Wonder" title="Stevie Wonder">Stevie Wonder</a>, and <a href="/wiki/Paul_McCartney" title="Paul McCartney">Paul McCartney</a>. Released in 1979, it was the first solo album to generate four U.S. top&#160;10 hits, including the chart-topping singles "<a href="/wiki/Don%27t_Stop_%27til_You_Get_Enough" title="Don't Stop 'til You Get Enough">Don't Stop 'til You Get Enough</a>" and "<a href="/wiki/Rock_with_You_(Michael_Jackson_song)" title="Rock with You (Michael Jackson song)">Rock with You</a>".<sup id="cite_ref-Nelson_George_overview_37-38_19-0" class="reference"><a href="#cite_note-Nelson_George_overview_37-38-19"><span>[</span>20<span>]</span></a></sup><sup id="cite_ref-MichaelJacksonIsBorn_20-0" class="reference"><a href="#cite_note-MichaelJacksonIsBorn-20"><span>[</span>21<span>]</span></a></sup> It reached number three on the <a href="/wiki/Billboard_200" title="Billboard 200"><i>Billboard</i> 200</a> and eventually sold over <span style="white-space:nowrap;">20 million</span> copies worldwide.<sup id="cite_ref-Off_the_Wall_.7B.7BNowrap.7C20_million.7D.7D_21-0" class="reference"><a href="#cite_note-Off_the_Wall_.7B.7BNowrap.7C20_million.7D.7D-21"><span>[</span>22<span>]</span></a></sup> In 1980, Jackson won three awards at the <a href="/wiki/American_Music_Awards" title="American Music Awards" class="mw-redirect">American Music Awards</a> for his solo efforts: Favorite Soul/R&amp;B Album, Favorite Soul/R&amp;B Male Artist, and Favorite Soul/R&amp;B Single for "Don't Stop 'Til You Get Enough".<sup id="cite_ref-AMAs_1980_22-0" class="reference"><a href="#cite_note-AMAs_1980-22"><span>[</span>23<span>]</span></a></sup><sup id="cite_ref-AMAs_1980_2_23-0" class="reference"><a href="#cite_note-AMAs_1980_2-23"><span>[</span>24<span>]</span></a></sup> That year, he also won <a href="/wiki/Billboard_Year-End" title="Billboard Year-End">Billboard Year-End</a> for Top Black Artist and Top Black Album and a Grammy Award for Best Male R&amp;B Vocal Performance, also for "Don't Stop 'Til You Get Enough".<sup id="cite_ref-Nelson_George_overview_37-38_19-1" class="reference"><a href="#cite_note-Nelson_George_overview_37-38-19"><span>[</span>20<span>]</span></a></sup> Jackson again won at the American Music Awards in 1981 for Favorite Soul/R&amp;B Album and Favorite Soul/R&amp;B Male Artist.<sup id="cite_ref-AMAs_1981_24-0" class="reference"><a href="#cite_note-AMAs_1981-24"><span>[</span>25<span>]</span></a></sup> Despite its commercial success, Jackson felt <i>Off the Wall</i> should have made a much bigger impact, and was determined to exceed expectations with his next release.<sup id="cite_ref-25" class="reference"><a href="#cite_note-25"><span>[</span>26<span>]</span></a></sup> In 1980, he secured the highest <a href="/wiki/Royalties" title="Royalties">royalty</a> rate in the music industry: 37 percent of wholesale album profit.<sup id="cite_ref-26" class="reference"><a href="#cite_note-26"><span>[</span>27<span>]</span></a></sup></p> 

<p>This text is from the wikipedia article about <a href="http://en.wikipedia.org/wiki/Michael_jackson">Michael Jackson</a></p>
""",
"""
<h1>The duck family</h1>
<p>The <b>Duck family</b> is a <a href="/wiki/Fictional_character" title="Fictional character" class="mw-redirect">fictional</a> family created by <a href="/wiki/The_Walt_Disney_Company" title="The Walt Disney Company">The Walt Disney Company</a>. Its best known member is <a href="/wiki/Donald_Duck" title="Donald Duck">Donald Duck</a>.</p> 
<p>In the early 1950s <a href="/wiki/Carl_Barks" title="Carl Barks">Carl Barks</a> was in his second decade of creating <a href="/wiki/Comic_book" title="Comic book">comic book</a> stories starring <a href="/wiki/Donald_Duck" title="Donald Duck">Donald Duck</a> and his various relatives. He had personally created several of the latter. <a href="/wiki/Scrooge_McDuck" title="Scrooge McDuck">Scrooge McDuck</a> and <a href="/wiki/Gladstone_Gander" title="Gladstone Gander" class="mw-redirect">Gladstone Gander</a> being the most notable among them. But the exact relation between them was still somewhat uncertain. Carl decided to create a personal version of their <a href="/wiki/Family_tree" title="Family tree">Family tree</a>. To better define their relations he added several previously unknown relatives. Carl never intended to publish this family tree as he had created it for personal use.</p> 
<p>In 1981 Carl was well into his retirement but his stories remained popular and had gained him unexpected fame. He had given several interviews and answered questions about his personal views on the characters and their stories. Among other subjects, Carl described his early version of the family tree. Rough sketches of the tree were published in a number of <a href="/wiki/Fanzine" title="Fanzine">fanzines</a>. Fans of the characters were pleased for the background it added to them. At this point <a href="/w/index.php?title=Mark_Worden&amp;action=edit&amp;redlink=1" class="new" title="Mark Worden (page does not exist)">Mark Worden</a> decided to create a drawing of this family tree including portraits of the characters mentioned. Otherwise Mark made few changes to the tree, most notably adding <a href="/wiki/Daisy_Duck" title="Daisy Duck">Daisy Duck</a> as Donald's main love interest. His illustrated version of the tree was published at first in several fanzines and later in the Carl Barks Library. The later was a ten-volume collection of his works in hardcover black-and-white edition.</p> 
<p>In 1987 <a href="/wiki/Don_Rosa" title="Don Rosa">Don Rosa</a>, a long-time fan of Carl Barks and personal friend of Mark Worden, started creating his own stories featuring <a href="/wiki/Scrooge_McDuck" title="Scrooge McDuck">Scrooge McDuck</a> and his various associates. His stories contained numerous references to older stories by Carl as well as several original ideas. After several years he gained a fanbase of his own. In the early 1990s <a href="/wiki/Egmont_(media_group)" title="Egmont (media group)" class="mw-redirect">Egmont</a>, the publishing house employing Don, offered him an ambitious assignment. He was to create the definitive version of Scrooge's biography and a family tree accompanying it. This was supposed to end decades of contradictions between stories which caused confusion to readers. The project was to become <a href="/wiki/The_Life_and_Times_of_Scrooge_McDuck" title="The Life and Times of Scrooge McDuck">The Life and Times of Scrooge McDuck</a>. The family tree accompanying it was first published in <a href="/wiki/Norway" title="Norway">Norway</a> on July 3, 1993.</p> 
<p>In the process of working on Scrooge's biography, Don studied Barks' old stories mentioning his past. Then he added several ideas of his own. Among them were biographical information for Scrooge's supporting cast. In a way Scrooge's biography was also their own biography.</p> 

<h2>Duck family members featured in the Family Tree</h2> 
<h3>Pintail Duck</h3> 
<p><b>Pintail Duck</b> first appeared in the story called Back to Long Ago which first appeared in <a href="/wiki/Uncle_Scrooge" title="Uncle Scrooge">Uncle Scrooge</a> #16. In that story it was revealed that he and his friend Matey <a href="/wiki/Malcolm_McDuck" title="Malcolm McDuck" class="mw-redirect">Malcolm McDuck</a> buried a treasure of <a href="/wiki/Potato" title="Potato">potatoes</a> for Captain Loyal Hawk of The Falcon Rover. He drowned three days later and was reborn as his descendant <a href="/wiki/Donald_Duck" title="Donald Duck">Donald Duck</a>.</p> 
<p><a href="/wiki/Don_Rosa" title="Don Rosa">Don Rosa</a> used Pintail in his version of The Donald Duck Family Tree, as the oldest Duck Family member on the tree.</p> 
<h3>Humperdink Duck</h3> 
<p><b>Humperdink Duck</b> is the late husband of <a href="/wiki/Grandma_Duck" title="Grandma Duck" class="mw-redirect">Grandma Duck</a> (Elvira Coot) and grandfather of <a href="/wiki/Donald_Duck" title="Donald Duck">Donald Duck</a>. He worked as a farmer in <a href="/wiki/Duckburg" title="Duckburg" class="mw-redirect">Duckburg</a>. He was the father of three children: Quackmore, Daphne, and Eider Duck. Humperdink Duck appears in person in <i><a href="/wiki/The_Life_and_Times_of_Scrooge_McDuck" title="The Life and Times of Scrooge McDuck">The Life and Times of Scrooge McDuck</a></i> and has been referred to in a few other stories. He was known as "Pa Duck". Unlike his wife Elvira, whose parents and even a brother were identified by <a href="/wiki/Don_Rosa" title="Don Rosa">Don Rosa</a>, who also decided she's the granddaughter of nothing less than the founder of <a href="/wiki/Duckburg" title="Duckburg" class="mw-redirect">Duckburg</a>, <a href="/wiki/Cornelius_Coot" title="Cornelius Coot" class="mw-redirect">Cornelius Coot</a>, Humperdink's past before having a family with Grandma keeps a mystery. According to Don Rosa, "the Duck family came from the British Isles, probably England".<sup id="cite_ref-0" class="reference"><a href="#cite_note-0"><span>[</span>1<span>]</span></a></sup></p> 
<p>In the story "<a href="https://coa.inducks.org/story.php?c=W+DD+++93-05" class="external text" rel="nofollow">The Good Old Daze</a>" by <a href="/wiki/Tony_Strobl" title="Tony Strobl">Tony Strobl</a>, one of the most beloved duck masters of all-time, Grandpa (Humperdink) appears in flashback taking care of little Donald along with Grandma.</p> 

<p>This text is from the wikipedia article about <a href="http://en.wikipedia.org/wiki/Duck_family_(Disney)">The Duck Family (Disney)</a></p>
""",
"""
Something useful should have been here, but I was <em>too</em> <strong>lazy</strong>.
"""]


current_feedback_index = [-1] # Use list to get an object which we can set to 0 
def get_feedback_text():
    current_feedback_index[0] += 1
    if current_feedback_index[0] >= len(FEEDBACK_TEMPLATES):
        current_feedback_index[0] = 0
    return FEEDBACK_TEMPLATES[current_feedback_index[0]]


def create_missing_users(usernames):
    for username in usernames:
        try:
            User.objects.get(username=username)
            logging.debug("User %s already exists." % username)
        except User.DoesNotExist, e:
            u = User(username=username, email="%s@example.com" % username)
            u.set_password("test")
            u.save()
            logging.info("        Created user %s." % username)

def autocreate_delivery(group):
    active_deadline = group.get_active_deadline()

    cand = group.candidates.all()[0]
    delivery = active_deadline.deliveries.create(delivered_by=cand, successful=True)
    delivery.add_file('helloworld.txt', ['hello cruel world'])
    delivery.add_file('helloworld.py', ['print "hello world"'])
    delivery.add_file('helloworld.java', [
        '// Too much code for a sane "hello world"'])

    others = Delivery.objects.filter(deadline__assignment_group=group).order_by("-number")
    if others.count() == 1:
        if active_deadline.deadline < datetime.now():
            if randint(0, 100) <= 30:
                # 30% chance to get the first delivery after the deadline
                offset = timedelta(minutes=-randint(1, 20))
                logging.info("                (deliveries after deadline)")
            else:
                offset = timedelta(hours=randint(0, 15),
                        minutes=randint(0, 59))
            delivery.time_of_delivery = active_deadline.deadline - offset
        else:
            # Deadline is in the future. Deliver a random time before
            # "now". They can not deliver more than 5 deliveries (see
            # create_example_deliveries_and_feedback), so if
            # we say 5*3 hours in the past as a minimum for the first
            # delivery, we will never get deliveries in the future
            offset = timedelta(hours=randint(15, 25),
                    minutes=randint(0, 59))
            delivery.time_of_delivery = datetime.now() - offset
    else:
        # Make sure deliveries are sequential
        last_delivery = others[1].time_of_delivery
        delivery.time_of_delivery = last_delivery + \
                timedelta(hours=randint(0, 2), minutes=randint(0,
                    59))
    delivery.save()
    return delivery

def autocreate_deliveries(group, numdeliveries):
    d = []
    for x in xrange(numdeliveries):
        d.append(autocreate_delivery(group))
    return d

def autocreate_feedback(delivery, group_quality_percent, max_percent, grade_maxpoints):
    grade_percent = randint(group_quality_percent, max_percent)
    points = int(round(grade_maxpoints*grade_percent / 100.0))

    assignment = delivery.deadline.assignment_group.parentnode
    examiner = delivery.deadline.assignment_group.examiners.all()[0]
    feedback = delivery.feedbacks.create(rendered_view=get_feedback_text(),
                                         saved_by=examiner.user, points=points,
                                         grade="g{0}".format(points),
                                         is_passing_grade=bool(points))
    logging.info('                Feedback: points={points}, is_passing_grade={is_passing_grade}'.format(**feedback.__dict__))
    return feedback

def autocreate_feedbacks(delivery, group_quality_percent, max_percent, grade_maxpoints):
    for x in xrange(randint(1, 3)):
        autocreate_feedback(delivery, group_quality_percent, max_percent, grade_maxpoints)


def create_example_assignmentgroup(assignment, students, examiners,
        groupname=None):
    """ Create a assignmentgroup with the given students and examiners.

    :param assignment: The :class:`devilry.core.models.Assignment` where
        you wish to create the group.
    :param students: List of usernames.
    :param examiners: List of usernames.
    :return: The created :class:`devilry.core.models.AssignmentGroup`.
    """
    group = assignment.assignmentgroups.create()
    for student in students:
        group.candidates.create(
                student=User.objects.get(username=student))
    for examiner in examiners:
        group.examiners.create(user=User.objects.get(username=examiner))
    #group.deadlines.create(deadline=deadline)
    logging.info("        Created {0} (id:{1})".format(group, group.id))
    return group

def create_example_deliveries_and_feedback(group, quality_percents,
                                           group_quality_percent,
                                           grade_maxpoints,
                                           deliverycountrange,
                                           deadline):
    group.deadlines.create(deadline=deadline)
    now = datetime.now()
    two_weeks_ago = now - timedelta(days=14)
    two_days_ago = now - timedelta(days=2)
    five_days_ago = now - timedelta(days=5)

    # Deadline in the future - about half has not yet delivered - no
    # feedback
    if deadline > now:
        if randint(0, 100) <= 50:
            logging.debug("Deadline in the future - not made "\
                    "any deliveries yet")
            return

    # Every C student and worst has a 5% chance of forgetting to
    # deliver
    elif group_quality_percent < quality_percents[1]:
        if randint(0, 100) <= 5:
            return

    numdeliveries = 1
    deliverycountrange_split = deliverycountrange.split('-', 1)
    if len(deliverycountrange) > 1:
        numdeliveries = randint(int(deliverycountrange_split[0]),
                                int(deliverycountrange_split[1]))
    else:
        numdeliveries = int(deliverycountrange[0])
    if numdeliveries == 0:
        return
    else:
        logging.info("                Deliveries: {numdeliveries}".format(numdeliveries=numdeliveries))
    deliveries = autocreate_deliveries(group, numdeliveries)
    delivery = deliveries[-1]

    # Determine grade. Everyone get a random grade within their "usual"
    # grade.
    max_percent = 100
    for p in quality_percents:
        if group_quality_percent > p:
            break
        max_percent = p

    # More than two weeks since deadline - should have feedback on about all
    if deadline < two_weeks_ago:
        logging.info("                Very old deadline (14 days +): Only 3% missing feedback (forgotten)")
        if randint(0, 100) <= 3: # Always a 3% chance to forget giving feedback.
            return
        autocreate_feedbacks(delivery, group_quality_percent, max_percent, grade_maxpoints)

    # Less than two weeks but more that 5 days since deadline
    elif deadline < five_days_ago:
        logging.info("                Old deadline (5-14 days): 10% of them has no feedback yet")
        if randint(0, 100) <= 10:
            # 10% of them has no feedback yet
            return
        autocreate_feedbacks(delivery, group_quality_percent, max_percent, grade_maxpoints)

    # Recent deadline (2-5 days since deadline)
    # in the middle of giving feedback
    elif deadline < two_days_ago:
        logging.info("                Recent deadline (2-5 days): 50% of them has no feedback yet")
        if randint(0, 100) <= 50:
            # Half of them has no feedback yet
            return
        autocreate_feedbacks(delivery, group_quality_percent, max_percent, grade_maxpoints)

    # Very recent deadline (0-2 days since deadline)
    elif deadline < now:
        logging.info("                Very recent deadline (0-3 days): 90% of them has no feedback yet")
        if randint(0, 100) <= 90:
            # 90% of them has no feedback yet
            return
        autocreate_feedbacks(delivery, group_quality_percent, max_percent, grade_maxpoints)

    # Deadline is in the future
    else:
        logging.info("                Deadline is in the future. Made deliveries, but "\
                "no feedback")
        pass # No feedback

def parse_deadline_profile(profile):
    if not (profile.startswith("-") or profile.startswith("+")):
        raise SystemExit("Invalid --deadline-profile")

    now = datetime.now()
    if not profile[1:].isdigit():
        raise SystemExit("Numeric deadline profile must be + or - "\
                "suffixed with a number")
    days = int(profile[1:])
    if profile.startswith("-"):
        deadline = now - timedelta(days=int(days))
    else:
        deadline = now + timedelta(days=int(days))
    return deadline

def parse_deadline_profiles(profiles):
    return [parse_deadline_profile(profile) for profile in profiles.split(',')]


def create_assignment(period, deadlines, **assignment_kwargs):
    """ Create an assignment from path. """
    assignment = period.assignments.create(publishing_time = deadlines[0] - timedelta(14),
                                           **assignment_kwargs)

    #assignment.gradeeditor_config.gradeeditorid='asminimalaspossible'
    #assignment.gradeeditor_config.config=json.dumps({'defaultvalue': True,
                                                     #'fieldlabel': 'Is the assignment approved?'})

    #assignment.gradeeditor_config.gradeeditorid = 'manual'
    #assignment.gradeeditor_config.config = None

    assignment.gradeeditor_config.gradeeditorid = 'approved'
    assignment.gradeeditor_config.config = None

    #assignment.gradeeditor_config.gradeeditorid = 'autograde'
    #grades = [["C", 65],["B", 80],["A", 93],["F", 0],["E", 30],["D", 45]]
    #assignment.gradeeditor_config.config = json.dumps({'maxpoints': 100,
                                                       #'approvedlimit': 30,
                                                       #'grades': grades,
                                                       #'pointlabel': 'Enter number of points earned',
                                                       #'feedbacklabel': 'Enter feedback'})

    assignment.gradeeditor_config.full_clean()
    assignment.gradeeditor_config.save()
    assignment.save()
    return assignment

def fit_assignment_in_parentnode(assignment, deadlines):
    """ Make sure assignment fits in parentnode """
    if assignment.parentnode.start_time > assignment.publishing_time:
        assignment.parentnode.start_time = assignment.publishing_time - \
                timedelta(days=5)
        assignment.parentnode.save()
    if assignment.parentnode.end_time < deadlines[-1]:
        assignment.parentnode.end_time = deadlines[-1] + timedelta(days=20)
        assignment.parentnode.save()


def grouplist(lst, n):
    l = len(lst)/n
    if len(lst)%n:
        l += 1
    for i in xrange(l):
        yield lst[i*n:i*n+n]

def create_groups(assignment,
                  deadlines, groupname_prefix,
                  all_examiners, examiners_per_group,
                  all_students, students_per_group,
                  deliverycountrange, grade_maxpoints):
    quality_percents = (
            93, # A > 93
            80, # B > 80
            65, # C > 65
            45, # D > 45
            30) # E > 30 

    examinersiter = itertools.cycle(grouplist(all_examiners, examiners_per_group))
    for studnum, students_in_group in enumerate(grouplist(all_students, students_per_group)):
        examiners_on_group = examinersiter.next()
        groupname = None
        if groupname_prefix:
            groupname = "%s %d" % (groupname_prefix, studnum)
        group = create_example_assignmentgroup(assignment, students_in_group,
                examiners_on_group, groupname)

        group_quality_percent = 100 - (float(studnum)/len(all_students)* 100)
        group_quality_percent = round(group_quality_percent)
        logging.debug("    Group quality percent: %s" % group_quality_percent)

        for deadline in deadlines:
            logging.info('            Deadline: {0}'.format(deadline))
            create_example_deliveries_and_feedback(group,
                                                   quality_percents,
                                                   group_quality_percent,
                                                   grade_maxpoints,
                                                   deliverycountrange,
                                                   deadline)

def create_numbered_users(numusers, prefix):
    users = ['{0}{1}'.format(prefix, number) for number in xrange(0, numusers)]
    create_missing_users(users)
    return users

def get_random_tags():
    available = ['tag1', 'tag2', 'supertag', 'tag3', 'special']
    tags = set()
    for x in xrange(randint(1, 2)):
        tags.add(available[randint(0, len(available)-1)])
    return ','.join(tags)

def add_relatedstudents(related, usernames):
    for username in usernames:
        try:
            relatedStudent = related.create(user=User.objects.get(username=username),
                                            candidate_id=username.replace('student', 'secretcand'),
                                            tags=get_random_tags())
            profile = relatedStudent.user.get_profile()
            profile.full_name = 'The ' + username.capitalize()
            profile.save()
        except IntegrityError:
            pass # We can not add duplicates

def add_relatedexaminers(related, usernames):
    for username in usernames:
        try:
            related.create(user=User.objects.get(username=username),
                           tags=get_random_tags())
        except IntegrityError:
            pass # We can not add duplicates

def create_example_assignment(period,
                              groupname_prefix = None,
                              deadline_profiles = '-10',

                              num_students = 10,
                              studentname_prefix = 'student',
                              students_per_group = 1,

                              num_examiners=3,
                              examinername_prefix='examiner',
                              examiners_per_group=1,

                              grade_maxpoints=1,
                              deliverycountrange='0-4',

                              **assignment_kwargs):
    """
    :param assignment_kwargs: Keyword arguments to Assignment.__init__.
    :param groupname_prefix:
        Group name prefix. Group names will be this prefix plus
        a number. If this is None, group name will be left blank.
    :param deadline_profiles:
        A list of deadline offsets. Example: "+10,-20,-35" will create
        a deadline 10 days in the future, a deadline 20 days ago, and
        a deadline 35 days ago.

    :param num_students: Total number of students.
    :param studentname_prefix: Prefix of student name.
    :param students_per_group: Number of students per group.

    :param num_examiners: Total number of examiners.
    :param studentname_prefix: Prefix of student name.
    :param examiners_per_group: Number of examiners per group.

    :param grade_maxpoints: Maxpoints for grades.
    :param deliverycountrange:
            Number of deliveries. If it is a range separated by '-',
            a random number of deliveries in this range is used.
    """
    deadlines = parse_deadline_profiles(deadline_profiles)
    assignment = create_assignment(period, deadlines, **assignment_kwargs)

    fit_assignment_in_parentnode(assignment, deadlines)

    logging.info("    Creating groups on {0}".format(assignment))
    all_examiners = create_numbered_users(num_examiners, examinername_prefix)
    all_students = create_numbered_users(num_students, studentname_prefix)
    add_relatedexaminers(period.relatedexaminer_set, all_examiners)
    add_relatedstudents(period.relatedstudent_set, all_students)
    create_groups(assignment,
                  deadlines = deadlines,
                  groupname_prefix = groupname_prefix,

                  all_examiners = all_examiners,
                  examiners_per_group = examiners_per_group,

                  all_students = all_students,
                  students_per_group = students_per_group,

                  grade_maxpoints = grade_maxpoints,
                  deliverycountrange = deliverycountrange)
