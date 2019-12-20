from django.test import TestCase
from .models import *


class ModelTestCase(TestCase):
    def test_model(self):
        test_spec_1 = Specialization.objects.update_or_create(name="Nurse")
        test_group_1, _ = CustomGroup.objects.update_or_create(name="Nurse-A", specialization=test_spec_1)
        test_group_2, _ = CustomGroup.objects.update_or_create(name="Nurse-B", specialization=test_spec_1)
        test_user = CustomUser.objects.update_or_create(email="alice@gmail.com", certificate="G12345678", username="Alice", group=test_group_1)