from django.test import TestCase
from devilry.apps.core import testhelper
from ..utils import modelinstance_to_dict

from ..fieldspec import FieldSpec, OneToMany
from ..filterspec import FilterSpecs, FilterSpec, PatternFilterSpec


class TestSimplifiedUtils(TestCase, testhelper.TestHelper):

    def setUp(self):
        self.add(nodes='uni:admin(admin)',
                 subjects=['inf101', 'inf102'],
                 periods=['fall11', 'spring11'],
                 assignments=['a1', 'a2'],
                 assignmentgroups=['g1:candidate(stud1, stud2):examiner(exam1)',
                                   'g2:candidate(stud3):examiner(exam2)'],
                 deadlines=['d1:ends(10)'])

    def test_model_to_dict_assignment(self):
        _subject_long     = 'parentnode__parentnode__long_name'
        _subject_short    = 'parentnode__parentnode__short_name'
        _subject_id       = 'parentnode__parentnode'

        _period_long      = 'parentnode__long_name'
        _period_short     = 'parentnode__short_name'
        _period_id        = 'parentnode'

        _assignment_long  = 'long_name'
        _assignment_short = 'short_name'
        _assignment_id    = 'id'

        resultfields = FieldSpec(_assignment_long, _assignment_short, _assignment_id,
                                 period=[_period_short, _period_long, _period_id],
                                 subject=[_subject_long, _subject_short, _subject_id])

        # convert an assignment, a1, to a dict
        modeldict = modelinstance_to_dict(self.inf101_fall11_a1, resultfields.aslist(['period', 'subject']))

        # assert that there are the expected number of keys
        self.assertEquals(len(modeldict.keys()), 9)
        # and assert that all the fields are as expected
        # subject fields
        self.assertEquals(modeldict[_subject_long], self.inf101.long_name)
        self.assertEquals(modeldict[_subject_short], self.inf101.short_name)
        self.assertEquals(modeldict[_subject_id], self.inf101.id)

        # period fields
        self.assertEquals(modeldict[_period_long], self.inf101_fall11.long_name)
        self.assertEquals(modeldict[_period_short], self.inf101_fall11.short_name)
        self.assertEquals(modeldict[_period_id], self.inf101_fall11.id)

        # assignment fields
        self.assertEquals(modeldict[_assignment_long], self.inf101_fall11_a1.long_name)
        self.assertEquals(modeldict[_assignment_short], self.inf101_fall11_a1.short_name)
        self.assertEquals(modeldict[_assignment_id], self.inf101_fall11_a1.id)

        # convert another assignment, a2, this time without the extra
        # fields
        modeldict2 = modelinstance_to_dict(self.inf101_fall11_a2, resultfields.aslist())
        self.assertEquals(len(modeldict2.keys()), 3)

        # and that the fields are as expected
        self.assertEquals(modeldict2[_assignment_long], self.inf101_fall11_a2.long_name)
        self.assertEquals(modeldict2[_assignment_short], self.inf101_fall11_a2.short_name)
        self.assertEquals(modeldict2[_assignment_id], self.inf101_fall11_a2.id)


    def test_model_to_dict_assignmentgroup(self):
        resultfields = FieldSpec('id', OneToMany('candidates', fields=['full_name', 'email']))
        modeldict = modelinstance_to_dict(self.inf101_fall11_a1_g1, resultfields.aslist())
        self.assertEquals(modeldict['candidates'], [{'email': u'stud1@example.com', 'full_name': None},
                                                    {'email': u'stud2@example.com', 'full_name': None}])

        resultfields = FieldSpec('id', OneToMany('candidates', fields=['student__username', 'student__devilryuserprofile__full_name']))
        modeldict = modelinstance_to_dict(self.inf101_fall11_a1_g1, resultfields.aslist())
        self.assertEquals(modeldict['candidates'], [{'student__username': u'stud1', 'student__devilryuserprofile__full_name': None},
                                                    {'student__username': u' stud2', 'student__devilryuserprofile__full_name': None}])

    def test_fieldspec(self):
        fs1 = FieldSpec('value1', 'value2', group1=['groupval1', 'groupval2'])
        fs2 = FieldSpec('value3', 'value4', group1=['groupval3', 'groupval4'])

        # this should be fine. fs3 should be a brand new instance
        fs3 = fs1 + fs2
        self.assertFalse(fs1 is fs2)
        self.assertFalse(fs1 is fs3)
        self.assertFalse(fs2 is fs3)

        # Try adding fieldspecs with duplicate fields
        fs4 = FieldSpec('value1')
        with self.assertRaises(ValueError):
            fs3 + fs4

        # now with a duplicate value within the field_group
        fs5 = FieldSpec('value4', group1=['groupval1'])
        with self.assertRaises(ValueError):
            fs3 + fs5

    def test_filterspecs(self):
        f1 = FilterSpecs(FilterSpec('hello'),
                         PatternFilterSpec('test.*'),
                         FilterSpec('world'))
        with self.assertRaises(ValueError):
            f1 = FilterSpecs(FilterSpec('hello'),
                             FilterSpec('hello'))
        with self.assertRaises(ValueError):
            f1 = FilterSpecs(FilterSpec('hello'),
                             PatternFilterSpec('he.*'))

    def test_filterspecs_copy(self):
        f1 = FilterSpecs(FilterSpec('hello'),
                         PatternFilterSpec('test.*'),
                         FilterSpec('world'))
        f2 = FilterSpecs(FilterSpec('cruel'),
                         FilterSpec('stuff'),
                         PatternFilterSpec('^(hello)+__world'))
        fmerge = f1 + f2
        self.assertEquals(set(fmerge.filterspecs.keys()), set(('hello', 'world', 'cruel', 'stuff')))
        self.assertEquals(len(fmerge.patternfilterspecs), 2)
        self.assertEquals(fmerge.patternfilterspecs[0].fieldname, 'test.*')
        self.assertEquals(fmerge.patternfilterspecs[1].fieldname, '^(hello)+__world')

    def test_filterspecs_copy_error(self):
        with self.assertRaises(ValueError):
            fmerge = FilterSpecs(FilterSpec('hello')) + FilterSpecs(FilterSpec('hello'))
        with self.assertRaises(ValueError):
            fmerge = FilterSpecs(PatternFilterSpec('hello')) + FilterSpecs(PatternFilterSpec('hello'))
        with self.assertRaises(ValueError):
            fmerge = FilterSpecs(PatternFilterSpec('hello')) + FilterSpecs(FilterSpec('hello'))
