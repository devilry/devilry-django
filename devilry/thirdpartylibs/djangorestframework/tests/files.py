from django.test import TestCase
from django import forms
from devilry.thirdpartylibs.djangorestframework.compat import RequestFactory
from devilry.thirdpartylibs.djangorestframework.views import View
from devilry.thirdpartylibs.djangorestframework.resources import FormResource
import StringIO

class UploadFilesTests(TestCase):
    """Check uploading of files"""
    def setUp(self):
        self.factory = RequestFactory()

    def test_upload_file(self):

        class FileForm(forms.Form):
            file = forms.FileField()

        class MockView(View):
            permissions = ()
            form = FileForm

            def post(self, request, *args, **kwargs):
                return {'FILE_NAME': self.CONTENT['file'].name,
                        'FILE_CONTENT': self.CONTENT['file'].read()}

        file = StringIO.StringIO('stuff')
        file.name = 'stuff.txt'
        request = self.factory.post('/', {'file': file})
        view = MockView.as_view()
        response = view(request)
        self.assertEquals(response.content, '{"FILE_CONTENT": "stuff", "FILE_NAME": "stuff.txt"}')

