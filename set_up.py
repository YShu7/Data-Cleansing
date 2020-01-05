import sys
import os
import django


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'datacleansing.settings')
django.setup()

from authentication.models import *

Specialization.objects.all().delete()
test_spec_1, _ = Specialization.objects.update_or_create(name="Nurse")
test_spec_2, _ = Specialization.objects.update_or_create(name="General")
test_spec_3, _ = Specialization.objects.update_or_create(name="Nutrition")

CustomGroup.objects.all().delete()
test_group_11, _ = CustomGroup.objects.update_or_create(name="Nurse-A", main_group=test_spec_1)
test_group_12, _ = CustomGroup.objects.update_or_create(name="Nurse-B", main_group=test_spec_1)
test_group_21, _ = CustomGroup.objects.update_or_create(name="General-A", main_group=test_spec_2)
test_group_22, _ = CustomGroup.objects.update_or_create(name="General-B", main_group=test_spec_2)
test_group_23, _ = CustomGroup.objects.update_or_create(name="General-C", main_group=test_spec_2)
test_group_31, _ = CustomGroup.objects.update_or_create(name="Nutrition-A", main_group=test_spec_3)

CustomUser.objects.all().delete()
test_user = CustomUser.objects.create_user(email="alice@gmail.com", certificate="G12345678", username="Alice",
                                           group=test_group_11, password="alice")

for i in range(2):
    CustomUser.objects.create_user(email="{}@gmail.com".format(i), certificate="G1234567{}".format(i), username="Alice",
                                   group=test_group_11, password="{}".format(i))

test_admin = CustomUser.objects.create_superuser(email="admin@gmail.com", username="Admin", certificate="G00000000",
                                                 password="guy123456")

from pages.models import *

Type.objects.all().delete()
types = []
for i in range(5):
    type,  _ = Type.objects.update_or_create(type="Type_{}".format(i))
    types.append(type)

TaskData.objects.all().delete()

VotingData.objects.all().delete()
Choice.objects.all().delete()
for i in range(50):
    task_data, _ = TaskData.objects.update_or_create(question_text="Vote{}".format(i))
    voting_data, _ = VotingData.objects.update_or_create(question=task_data, type=types[i%len(types)], activate=True)
    for j in range(2):
        choice, _ = Choice.objects.update_or_create(data=voting_data, answer="Answer_{}{}".format(i, j), num_votes=0)

ValidatingData.objects.all().delete()
for i in range(50):
    task_data, _ = TaskData.objects.update_or_create(question_text="Val{}".format(i))
    validating_data,  _ = ValidatingData.objects.update_or_create(question=task_data,
                                                                  answer_text="A{}".format(i), type=types[i%len(types)])

from assign.models import Assignment
from assign.views import assign
assign(CustomUser, Assignment, 10, ValidatingData, TaskData)
assign(CustomUser, Assignment, 3, VotingData, TaskData)