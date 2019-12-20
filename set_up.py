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

for i in range(2):
    CustomUser.objects.create_user(email="{}@gmail.com".format(i), certificate="G1234567{}".format(i), username="Alice",
                                   group=test_group_1, password="{}".format(i))

test_admin = CustomUser.objects.create_superuser(email="admin@gmail.com", username="Admin", certificate="G00000000",
                                                 password="guy123456")

from pages.models import *

Type.objects.all().delete()
types = []
for i in range(5):
    type,  _ = Type.objects.update_or_create(type="Type_{}".format(i))
    types.append(type)

VotingData.objects.all().delete()
Choice.objects.all().delete()
for i in range(10):
    voting_data,  _ = VotingData.objects.update_or_create(question_text="Vote{}".format(i), type=types[i%len(types)], activate=True)
    for j in range(2):
        choice, _ = Choice.objects.update_or_create(data=voting_data, answer="Answer_{}".format(j), num_votes=0)

ValidatingData.objects.all().delete()
for i in range(10):
    validating_data,  _ = ValidatingData.objects.update_or_create(question_text="Val{}".format(i),
                                                                  answer_text="A{}".format(i), type=types[i%len(types)])

from assign.models import AssignmentValidate, AssignmentVote
from assign.views import assign
assign(CustomUser, ValidatingData, AssignmentValidate, 10)
assign(CustomUser, VotingData, AssignmentVote, 3)