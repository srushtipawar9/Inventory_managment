from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TestCase

from data.models import JCBPart


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


class EstimatePartPriceLookupTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='secret123')
        self.part = JCBPart.objects.create(
            part_number='MDG-001',
            name='Main Drive Gear',
            description='Main drive gear for JCB',
            price='1250.50',
            stock_quantity=10,
            category='POWERTRAIN',
        )

    def test_lookup_returns_price_case_insensitively(self):
        self.client.force_login(self.user)

        response = self.client.get('/estimate/part-price/', {'name': 'main drive gear'})

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content.decode('utf-8'), {'price': '1250.50'})

    def test_suggestions_return_matching_parts(self):
        self.client.force_login(self.user)
        JCBPart.objects.create(
            part_number='HOS-002',
            name='Hydraulic Hose',
            description='Hydraulic hose product',
            price='499.00',
            stock_quantity=4,
            category='HYDRAULICS',
        )

        response = self.client.get('/estimate/part-suggestions/', {'q': 'main'})

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(len(payload['results']), 1)
        self.assertEqual(payload['results'][0]['name'], 'Main Drive Gear')
