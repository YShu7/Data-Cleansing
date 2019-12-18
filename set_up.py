import sys
import os
import django

# 这两行很重要，用来寻找项目根目录，os.path.dirname要写多少个根据要运行的python文件到根目录的层数决定
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'datacleansing.settings')
django.setup()

from authentication.models import *

Specialization.objects.all().delete()
test_spec_1, _ = Specialization.objects.update_or_create(name="Nurse")

CustomGroup.objects.all().delete()
test_group_1, _ = CustomGroup.objects.update_or_create(name="Nurse-A", main_group=test_spec_1)
test_group_2, _ = CustomGroup.objects.update_or_create(name="Nurse-B", main_group=test_spec_1)

CustomUser.objects.all().delete()
test_user = CustomUser.objects.create_user(email="alice@gmail.com", certificate="G12345678", username="Alice",
                                           group=test_group_1, password="alice")

test_admin = CustomUser.objects.create_superuser(email="admin@gmail.com", username="Admin", certificate="G00000000",
                                                 password="guy123456")

from pages.models import *

Type.objects.all().delete()
test_type1,  _ = Type.objects.update_or_create(type="T1")
test_type2,  _ = Type.objects.update_or_create(type="T2")

VotingData.objects.all().delete()
test_voting_1,  _ = VotingData.objects.update_or_create(question_text="Vote1", type=test_type1, activate=True)
test_voting_2,  _ = VotingData.objects.update_or_create(question_text="Vote2", type=test_type2)

ValidatingData.objects.all().delete()
test_validating_1,  _ = ValidatingData.objects.update_or_create(question_text="Val1", answer_text="A1", type=test_type2)
test_validating_2,  _ = ValidatingData.objects.update_or_create(question_text="Val2", answer_text="A1")

Choice.objects.all().delete()
test_choice_11,  _ = Choice.objects.update_or_create(data=test_voting_1, answer="AC1", num_votes=1)
test_choice_12,  _ = Choice.objects.update_or_create(data=test_voting_1, answer="AC2", num_votes=0)