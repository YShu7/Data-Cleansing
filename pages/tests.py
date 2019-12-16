from django.test import TestCase
from .models import *


class ModelTestCase(TestCase):
    def test_model(self):
        test_type1, created = Type.objects.update_or_create(type="T1")
        test_type2, created = Type.objects.update_or_create(type="T2")
        print(Type.objects.all())

        test_voting_1, created = VotingData.objects.update_or_create(question_text="Vote1", type=test_type1)
        test_voting_2, created = VotingData.objects.update_or_create(question_text="Vote2", type=test_type2)
        print(VotingData.objects.all())

        test_validating_1, created = Data.objects.update_or_create(question_text="Val1", answer_text="A1", type=test_type2)
        test_validating_2, created = Data.objects.update_or_create(question_text="Val2", answer_text="A1")
        print(Data.objects.all())

        test_choice_11, created = Choice.objects.update_or_create(data=test_voting_1, answer="AC1", num_votes=1)
        test_choice_12, created = Choice.objects.update_or_create(data=test_voting_1, answer="AC2", num_votes=0)
        print(Choice.objects.all())

        test_choice_12.update(num_votes=6)
        print(Choice.objects.all())