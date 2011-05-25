from django.test import TestCase

from ..examiner import RestAssignments


class TestRestAssignments(TestCase):
    def test_getdata_to_kwargs(self):
        kw = RestAssignments._getdata_to_kwargs({'format':'json'})
        self.assertEquals(kw, dict(
                count=50, start=0, orderby=["short_name"],
                old=True, active=True, search=u'', longnamefields=False,
                pointhandlingfields=False, format='json'
            ))
