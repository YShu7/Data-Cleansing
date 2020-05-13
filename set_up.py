import os
import sys

import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'datacleansing.settings')
django.setup()

from assign.models import Assignment
from assign.views import assign
from authentication.models import *
from pages.models.models import *
from pages.models.validate import *
from pages.models.vote import *
from pages.models.image import *

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'datacleansing.settings')
django.setup()

Log.objects.all().delete()
Assignment.objects.all().delete()
Data.objects.all().delete()
VotingData.objects.all().delete()
Choice.objects.all().delete()
ValidatingData.objects.all().delete()
FinalizedData.objects.all().delete()
CustomGroup.objects.all().delete()
CustomUser.objects.all().delete()

# Create Groups

file = open('users.txt', 'r')
lines = file.read().splitlines()
group_names = lines[0].split(',')
group_loop = 0
groups = []

for line in lines[1:]:
    if (group_loop < len(group_names) and line == group_names[group_loop]):
        group, _ = CustomGroup.objects.update_or_create(name=group_names[group_loop])
        groups.append(group)
        group_loop += 1
    else:
        info = line.split(' ')
        if info[0] == "S":
            superuser = CustomUser.objects.create_superuser(email=info[1], certificate=info[2],
                                                            username=info[3], password=info[4])
            continue

        group = groups[group_loop-1]
        if info[0] == "U":
            user = CustomUser.objects.create_user(email=info[1], certificate=info[2],
                                                  username=info[3], group=group, password=info[4])
            if info[-1] == "Active":
                user.activate(True)
            else:
                user.activate(False)
            if info[-2] == "Approve":
                user.approve(True)
            else:
                user.approve(False)
        elif info[0] == "A":
            admin = CustomUser.objects.create_admin(email=info[1], certificate=info[2],
                                                    username=info[3], group=group, password=info[4])

        with open('voting.json') as f:
            voting_qas = json.load(f)
        for i, q in enumerate(voting_qas):
            voting_data = VotingData.create(title=q, group=group, is_active=True)
            if i < 2:
                for a in voting_qas[q]:
                    choice, _ = Choice.objects.update_or_create(data=voting_data, answer=a, num_votes=10)
                    voting_data.num_votes += 10
                voting_data.save()
            else:
                for a in voting_qas[q]:
                    choice, _ = Choice.objects.update_or_create(data=voting_data, answer=a, num_votes=0)

        with open('validating.json') as f:
            validating_qas = json.load(f)
        for i, q in enumerate(validating_qas):
            a = validating_qas[q]
            for i in range(5):
                validating_data = ValidatingData.create(title="{}-{}".format(i, q), group=group, ans=a)

        for q in validating_qas:
            finalized_data = FinalizedData.create(title="finalized_{}".format(q), group=group, ans=validating_qas[q])

        for filename in os.listdir('pages/static/images'):
            if filename.startswith('.'):
                continue
            data = ImageData.create(group=group, url="/static/images/{}".format(filename), title='{}/static/images/{}'.format(group.name, filename))
            for j in range(5):
                ImageLabel.objects.update_or_create(image=data, label="food{}".format(j))

for group in groups:
    users = CustomUser.objects.filter(is_active=True, is_approved=True, is_admin=False, group=group)
    print("validating: {}, voting: {}, user: {}".format(len(validating_qas), len(voting_qas), len(users)))
    assign(users, Assignment, ValidatingData.objects.filter(group=group), Data, num_user_per_task=3)
    assign(users, Assignment, VotingData.objects.filter(is_active=True, num_votes__lte=15, group=group), Data, num_user_per_task=5)
    assign(users, Assignment, FinalizedData.objects.filter(group=group), Data, num_user_per_task=3)
    assign(users, Assignment, ImageData.objects.filter(group=group), Data, num_user_per_task=3)