from django.test import TestCase
from django.contrib.auth.models import User

from devilry.core.models import Period

from views import _iter_periodstats


class TestViewhelpers(TestCase):
    fixtures = ['tests/gradestats/data.json']

    def test_iter_periodstats(self):
        p = Period.objects.get(short_name='looong',
                parentnode__short_name='inf1100')
        student2 = User.objects.get(username='student2')
        ps = [x for x in _iter_periodstats(p, student2)]
        #for p, g in ps:
            #print p
            #for grade in g:
                #print "   ", grade

        self.assertEquals(len(ps), 2)
        approvedgrade = ps[0]
        self.assertEquals(approvedgrade[0].get_key(),
                'grade_approved:approvedgrade')
        self.assertEquals(approvedgrade[2][0][0].get_candidates(),
                'student2, student3')
        self.assertEquals(approvedgrade[2][0][1],
                'Not approved')

        rstschemagrade = ps[1]
        self.assertEquals(rstschemagrade[0].get_key(),
                'grade_rstschema:rstschemagrade')
        self.assertEquals(rstschemagrade[2][1][0].get_candidates(),
                'student2, student3')
        self.assertEquals(rstschemagrade[2][1][1],
                '100.00% (9/9)')
