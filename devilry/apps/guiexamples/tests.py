from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse


class RestUserTest(TestCase):
    fixtures = ["tests/guiexamples/users.json"]

    def test_get(self):
        #url = reverse("devilry.guiexamples.RestUsers",
                #kwargs=dict(username="student1"))
        url = reverse("devilry-guiexamples-assignment_avg_labels")
        c = Client()
        c.login(username="student1", password="test")

        r = c.get(url)
        print r.content
        #self.assertTrue("Statistics for student0 in duck1100.h01" in r.content)
        #self.assertContains(r, "No deliveries", 1)
