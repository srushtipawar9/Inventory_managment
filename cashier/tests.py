from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TestCase


class MultipartRequestCompatibilityTests(TestCase):
    def test_multipart_request_is_parsed(self):
        factory = RequestFactory()
        uploaded_file = SimpleUploadedFile(
            'test.txt',
            b'hello world',
            content_type='text/plain',
        )

        request = factory.post(
            '/upload/',
            data={'name': 'sample', 'file': uploaded_file},
        )

        self.assertEqual(request.POST['name'], 'sample')
        self.assertEqual(request.FILES['file'].read(), b'hello world')
