from rest_framework.test import APIClient, APITestCase


class ConsultationAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        # Создать необходимые объекты для тестирования
