.. _testhelper:

================================================================
devilry.apps.core.testhelper --- Create core test data
================================================================


.. deprecated:: 1.4
    Use :doc:`devilry_developer.teshelpers.corebuilder` instead.


Example
#######

::

    from devilry.apps.core.testhelper import TestHelper

    testhelper = TestHelper()

    testhelper.add(nodes='uni:admin(mortend)',
             subjects=['cs101:admin(admin1,admin2):ln(Basic OO programming)',
                       'cs110:admin(admin3,admin4):ln(Basic scientific programming)',
                       'cs111:admin(admin1,damin3):ln(Advanced OO programming)'],
             periods=['fall11', 'spring11:begins(6)'])

    # add 4 assignments to inf101 and inf110 in fall and spring
    testhelper.add(nodes='uni',
             subjects=['cs101', 'cs110'],
             periods=['fall11', 'spring11'],
             assignments=['a1', 'a2'])

    # add 12 assignments to inf111 fall and spring.
    testhelper.add(nodes='uni',
             subjects=['cs111'],
             periods=['fall11', 'spring11'],
             assignments=['week1', 'week2', 'week3', 'week4'])

    # set up some students with descriptive names

    # inf101 is so easy, everyone passes
    testhelper.add_to_path('uni;cs101.fall11.a1.g1:candidate(goodStud1):examiner(examiner1).dl:ends(5)')
    testhelper.add_to_path('uni;cs101.fall11.a1.g2:candidate(goodStud2):examiner(examiner1).dl:ends(5)')
    testhelper.add_to_path('uni;cs101.fall11.a1.g3:candidate(badStud3):examiner(examiner2).dl:ends(5)')
    testhelper.add_to_path('uni;cs101.fall11.a1.g4:candidate(okStud4):examiner(examiner2).dl:ends(5)')

    testhelper.add_to_path('uni;cs101.fall11.a2.g1:candidate(goodStud1):examiner(examiner1).dl:ends(5)')
    testhelper.add_to_path('uni;cs101.fall11.a2.g2:candidate(goodStud2):examiner(examiner1).dl:ends(5)')
    testhelper.add_to_path('uni;cs101.fall11.a2.g3:candidate(badStud3):examiner(examiner2).dl:ends(5)')
    testhelper.add_to_path('uni;cs101.fall11.a2.g4:candidate(okStud4):examiner(examiner2).dl:ends(5)')

    # inf110 is an easy group-project, everyone passes
    testhelper.add_to_path('uni;cs110.fall11.a1.g1:candidate(goodStud1,goodStud2):examiner(examiner1).dl:ends(14)')
    testhelper.add_to_path('uni;cs110.fall11.a1.g2:candidate(badStud3,okStud4):examiner(examiner2).dl.ends(14)')

    testhelper.add_to_path('uni;cs110.fall11.a2.g1:candidate(goodStud1,goodStud2):examiner(examiner1).dl:ends(14)')
    testhelper.add_to_path('uni;cs110.fall11.a2.g2:candidate(badStud3,okStud4):examiner(examiner2).dl.ends(14)')

    # inf111 is hard! Everyone passes week1
    testhelper.add_to_path('uni;cs111.fall11.week1.g1:candidate(goodStud1):examiner(examiner3).dl:ends(5)')
    testhelper.add_to_path('uni;cs111.fall11.week1.g2:candidate(goodStud2):examiner(examiner3).dl:ends(5)')
    testhelper.add_to_path('uni;cs111.fall11.week1.g3:candidate(badStud3):examiner(examiner3).dl:ends(5)')
    testhelper.add_to_path('uni;cs111.fall11.week1.g4:candidate(okStud4):examiner(examiner3).dl:ends(5)')

    # and 2
    testhelper.add_to_path('uni;cs111.fall11.week2.g1:candidate(goodStud1):examiner(examiner3).dl:ends(5)')
    testhelper.add_to_path('uni;cs111.fall11.week2.g2:candidate(goodStud2):examiner(examiner3).dl:ends(5)')
    testhelper.add_to_path('uni;cs111.fall11.week2.g3:candidate(badStud3):examiner(examiner3).dl:ends(5)')
    testhelper.add_to_path('uni;cs111.fall11.week2.g4:candidate(okStud4):examiner(examiner3).dl:ends(5)')

    # badStud4 fails at week3
    testhelper.add_to_path('uni;cs111.fall11.week3.g1:candidate(goodStud1):examiner(examiner3).dl:ends(5)')
    testhelper.add_to_path('uni;cs111.fall11.week3.g2:candidate(goodStud2):examiner(examiner3).dl:ends(5)')
    testhelper.add_to_path('uni;cs111.fall11.week3.g4:candidate(okStud2):examiner(examiner3).dl:ends(5)')

    # and okStud4 fails at week4
    testhelper.add_to_path('uni;cs111.fall11.week4.g1:candidate(goodStud1):examiner(examiner3).dl:ends(5)')
    testhelper.add_to_path('uni;cs111.fall11.week4.g2:candidate(goodStud2):examiner(examiner3).dl:ends(5)')

    # deliveries
    goodFile = {'good.py': ['print ', 'awesome']}
    okFile = {'ok.py': ['print ', 'meh']}
    badFile = {'bad.py': ['print ', 'bah']}

    # cs101
    testhelper.add_delivery('cs101.fall11.a1.g1', goodFile)
    testhelper.add_delivery('cs101.fall11.a1.g2', goodFile)
    testhelper.add_delivery('cs101.fall11.a1.g3', badFile)
    testhelper.add_delivery('cs101.fall11.a1.g4', okFile)
    testhelper.add_delivery('cs101.fall11.a2.g1', goodFile)
    testhelper.add_delivery('cs101.fall11.a2.g2', goodFile)
    testhelper.add_delivery('cs101.fall11.a2.g3', badFile)
    testhelper.add_delivery('cs101.fall11.a2.g4', okFile)

    # cs110
    testhelper.add_delivery('cs110.fall11.a1.g1', goodFile)
    testhelper.add_delivery('cs110.fall11.a1.g1', goodFile)
    testhelper.add_delivery('cs110.fall11.a2.g2', badFile)
    testhelper.add_delivery('cs110.fall11.a2.g2', okFile)

    # cs111
    testhelper.add_delivery('cs111.fall11.week1.g1', goodFile)
    testhelper.add_delivery('cs111.fall11.week1.g2', goodFile)
    testhelper.add_delivery('cs111.fall11.week1.g3', badFile)
    testhelper.add_delivery('cs111.fall11.week1.g4', okFile)

    # g3's delivery fails here
    testhelper.add_delivery('cs111.fall11.week2.g1', goodFile)
    testhelper.add_delivery('cs111.fall11.week2.g2', goodFile)
    testhelper.add_delivery('cs111.fall11.week2.g3', badFile)
    testhelper.add_delivery('cs111.fall11.week2.g4', okFile)

    # g4's delivery fails here
    testhelper.add_delivery('cs111.fall11.week3.g1', goodFile)
    testhelper.add_delivery('cs111.fall11.week3.g2', goodFile)
    testhelper.add_delivery('cs111.fall11.week3.g4', okFile)

    # g4 fails
    testhelper.add_delivery('cs111.fall11.week4.g1', goodFile)
    testhelper.add_delivery('cs111.fall11.week4.g2', goodFile)

    # feedbacks
    #   an empty verdict defaults to max score
    goodVerdict = None
    okVerdict = {'grade': 'C', 'points': 85, 'is_passing_grade': True}
    badVerdict = {'grade': 'E', 'points': 60, 'is_passing_grade': True}
    failVerdict = {'grade': 'F', 'points': 30, 'is_passing_grade': False}

    testhelper.add_feedback('cs101.fall11.a1.g1', verdict=goodVerdict)
    testhelper.add_feedback('cs101.fall11.a1.g2', verdict=goodVerdict)
    testhelper.add_feedback('cs101.fall11.a1.g3', verdict=badVerdict)
    testhelper.add_feedback('cs101.fall11.a1.g4', verdict=okVerdict)
    testhelper.add_feedback('cs101.fall11.a2.g1', verdict=goodVerdict)
    testhelper.add_feedback('cs101.fall11.a2.g2', verdict=goodVerdict)
    testhelper.add_feedback('cs101.fall11.a2.g3', verdict=badVerdict)
    testhelper.add_feedback('cs101.fall11.a2.g4', verdict=okVerdict)

    # cs110
    testhelper.add_feedback('cs110.fall11.a1.g1', verdict=goodVerdict)
    testhelper.add_feedback('cs110.fall11.a1.g1', verdict=badVerdict)
    testhelper.add_feedback('cs110.fall11.a2.g2', verdict=goodVerdict)
    testhelper.add_feedback('cs110.fall11.a2.g2', verdict=okVerdict)

    # cs111
    testhelper.add_feedback('cs111.fall11.week1.g1', verdict=goodVerdict)
    testhelper.add_feedback('cs111.fall11.week1.g2', verdict=goodVerdict)
    testhelper.add_feedback('cs111.fall11.week1.g3', verdict=badVerdict)
    testhelper.add_feedback('cs111.fall11.week1.g4', verdict=okVerdict)

    # g3's feedback fails here
    testhelper.add_feedback('cs111.fall11.week2.g1', verdict=goodVerdict)
    testhelper.add_feedback('cs111.fall11.week2.g2', verdict=goodVerdict)
    testhelper.add_feedback('cs111.fall11.week2.g3', verdict=failVerdict)
    testhelper.add_feedback('cs111.fall11.week2.g4', verdict=okVerdict)

    # g4's feedback fails here
    testhelper.add_feedback('cs111.fall11.week3.g1', verdict=goodVerdict)
    testhelper.add_feedback('cs111.fall11.week3.g2', verdict=goodVerdict)
    testhelper.add_feedback('cs111.fall11.week3.g4', verdict=failVerdict)

    # g4 fails
    testhelper.add_feedback('cs111.fall11.week4.g1', verdict=goodVerdict)
    testhelper.add_feedback('cs111.fall11.week4.g2', verdict=goodVerdict)


TestHelper API
##############

.. currentmodule:: devilry.apps.core.testhelper
.. autoclass:: devilry.apps.core.testhelper.TestHelper
