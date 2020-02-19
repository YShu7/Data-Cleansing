import os
import sys

import django

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
group_names = ["KKH", "TPH", "AAH", "BH"]
groups = []
for group_name in group_names:
    group, _ = CustomGroup.objects.update_or_create(name=group_name)
    groups.append(group)

# Create Users
test_user = CustomUser.objects.create_user(email="alice@gmail.com", certificate="G12345678", username="Alice",
                                           group=groups[0], password="alice")
test_user.approve(True)

for i in range(2):
    user = CustomUser.objects.create_user(email="1{}@gmail.com".format(i), certificate="G1234567{}".format(i),
                                          username="Alice", group=groups[0], password="{}".format(i))
    user.approve(True)

for i in range(2):
    user = CustomUser.objects.create_user(email="2{}@gmail.com".format(i), certificate="G2234567{}".format(i),
                                          username="Alice", group=groups[1], password="{}".format(i))
    user.approve(True)
inactive_user = CustomUser.objects.create_user(email="inactive@gmail.com", certificate="G11111111",
                                               username="Inactive", group=groups[0], password="inactive")
inactive_user.approve(True)
inactive_user.activate(False)

pending_user = CustomUser.objects.create_user(email="pending@gmail.com", certificate="G99999999",
                                              username="Pending", group=groups[0], password="pending")

test_admin = CustomUser.objects.create_admin(email="admin@gmail.com", username="Admin", certificate="G00000000",
                                             group=groups[0], password="admin")
test_superuser = CustomUser.objects.create_superuser(email="superuser@gmail.com", username="SuperUser",
                                                     certificate="", password="superuser")

# Create VotingData
voting_qas = {
    """
    I have competing offers from startups with 190k base and ~400k equity - all vesting over four years. 
    Does anyone have an explanation?
    """: [
        """
        I have worked at Google (Mountain View) for 4 years. 
        I started at T4 (and remain at T4 still despite great performance reviews — promotion is non-trivial!)
        My initial offer had more stock, and Google’s stock price has done very well since the initial grant was made. 
        I automatically sell my stock as soon as it vests. My approximate total annual income has been:
        """,
        """
        My income in years 3 and 4 was (I think) higher than typical for T4 due to the strength of the stock price. 
        In year 5, unfortunately, I will see a whopping 65k reduction in gross income, 
        so I’ll be back to my year 3 salary, 
        because the annual extra stock grants haven’t been keeping up with the size of the initial stock grant, 
        and because I haven’t been promoted. 
        Promotion seems required to maintain a level salary from year 4 to year 5.
        """,
        """
        The reason it looks too low is because your source of data looks too high, at least based on what I know.
        I was just looking at Paysa this morning. 
        On the bright side, I think it’s an interesting site with a lot of potential. 
        On the down side, for the companies I know anything about (which includes Google), 
        it looks like they’re quoting compensation well above the mid-line, at least for the levels I know about.
        offer sounds alright to me, though the stock is a bit low.
        """
    ],
    "What's a meaningful resolution I can make (and actually keep) for 2020?": [
        """
        You've likely made a resolution in the past that turned out... well, 
        let's just say it didn't turn out so well. 😞
        Not this year!
        My recommendation? Resolve to take back control of your personal data online. 
        Most people believe that control of their personal data is broken, 
        but don't know what to do to fix it, or worse, think they can’t do anything to fix it. 
        I’m here to tell you that you can achieve this meaningful resolution through a few quick steps, 
        each of which make a huge difference protecting your privacy: 
        from stopping big tech from sucking up all your browsing data, 
        to adding extra protection to your passwords and email. 
        And, once set up, unlike going to the gym or mastering a new skill, it doesn’t take much effort to maintain.
        So, let’s make 2020 the year we take back our online privacy!
        """,
        """
        Step 1. Update your software
        Software on devices like phones, tablets and computers gets out-of-date over time, 
        and old software can contain security bugs or settings that leak personal data. 
        To reduce your exposure to these privacy risks, check for updates to your apps and operating systems, 
        and even better, set them to update automatically.
        That way you'll always have the latest, safest versions.
        """,
        """
        Step 2. Update your privacy settings
        Now that you have the latest software, dig into the latest privacy settings and update them. 
        Here are step-by-step instructions for all the major device types.
        Make sure you also go in and adjust per-app location settings, 
        so that your location history isn’t leaking where it shouldn’t. 
        For bonus points, review the apps you have installed. 
        If there are any you haven't used for a while, 
        remove them to reduce the chance of your personal data being shared.
        """
    ],
    "Who are some people that simply don't deserve the fame they have/had?": [
        """
        Well, there’s the fact that she dated someone who was 17 when she was 14. 
        Then the fact that she photo shops all her pictures that she uploads online. 
        Oh, and there’s this controversy with her actual age, 
        because some people have proof that she could be lying about her age. 
        She claims to be 15 now, but some people are saying there’s evidence that proves she’s actually 13 years old. 
        Feel free to look that up, if you wish.
        """,
        """
        Recently, she has claimed to have gotten pregnant with her boyfriend Mikey Tua. 
        Whether she’s telling the truth, I don’t know. To me, it seems like a big publicity stunt. 
        Maybe in a couple months, she’ll be coming out with news that she had a miscarriage. 
        This could be her way of covering up the fact that she wasn’t actually pregnant in the first place.
        """
    ],
    "What is a brain teaser that is very short and extremely hard for adults?": [
        """
        I was asked this question during an interview. Some of you might have heard a slight variation of it.
        There are 8 non-reactive chemicals out of which one is poisonous. You have three lab rats to test them on. 
        The poison takes 10 mins to work.
        How will you find out which is the poisonous chemical in the least possible time?
        """,
        """
        We feed the rats the chemicals according to the above table. 
        So, the first rat is given Chemicals 5,6,7,8 while the second rat is fed 
        Chemicals 3,4,7,8 and the final rat is given Chemicals 2,4,6,8. 
        After 10 minutes, according to the table, if the 3rd rat dies, Chemical 2 is poisoned. 
        If both the 1st and the 3rd rats die, the poisonous chemical is number 6. And so on. 
        If no rat dies, its Chemical 1!
        """
    ]
}

for q in voting_qas:
    voting_data = VotingData.create(title=q, group=groups[0], is_active=True)
    for a in voting_qas[q]:
        choice, _ = Choice.objects.update_or_create(data=voting_data, answer=a, num_votes=0)

validating_qns = [
    "What is the least intelligent thing you've ever seen a tourist do?",
    "What is the most intelligent thing you've ever seen a tourist do?",
    "What people are living proof that size doesn't matter?",
    "Who was the rudest celebrity you’ve met?",
    "Does the universe work physically?"
]
validating_ans = [
    """
    I spent a lot of time in the tourist areas of Niagara Falls.
    There are three separate waterfalls. The largest is the Horseshoe Falls, pictured down below.
    There is a huge park along the river, and it is freely accessible to anyone. 
    You can actually drive to within a few hundred meters/yards of the brink on the Canadian side (but it gets crowded).
    Along most of the Canadian side of the river, there is only a stone fence, with a metal railing. 
    Here is a photo taken right at the edge of the larger Horseshoe Falls.
    """,
    """
    I swear the following story is true…
    I went on a guided 4 x 4 tour in some of the natural parks of Botswana, 
    Namibia and Zimbabwe with some other folks a while back. 
    Our guide was a pretty tough looking fellow who was very well versed in the natural world. 
    He was happy to point out the various flora and fauna that we passed as we drove through the parks and, 
    at one point, 
    were poled along the Okavango swamps in low canoes called mokoros.
    """,
    """
    Size does matter.
    If someone tells you it’s an issue for them, it is. And this is an issue I hear about often.
    I’m sure there are lots of interesting and even inspiring stories that relate to this question,
    but I’m not going to tell you one.
    """,
    """
    I wish this question asked which celebrity was the nicest because that would be easy.
    In a former career, I worked in a variety of post-production roles at a Hollywood movie studio 
    where I met and worked with several celebrities.
    So before I tell you the rudest, let me tell you a few highlights of some of the nicest.
    """,
    """
    To my limited understanding and knowledge yes. I think the universe supports itself. 
    Not everything is known about even simple phenomenon but how the world functions
    in general is not some grand mystery. 
    We in general can see a pattern to how moat things work to where we can say it's not magic 
    there is a logical explanation to something.
    """
]

for q, a in zip(validating_qns, validating_ans):
    for i in range(5):
        validating_data = ValidatingData.create(title="{}-{}".format(i, q), group=groups[0], ans=a)

for q, a in zip(validating_qns, validating_ans):
    finalized_data = FinalizedData.create(title="finalized_{}".format(q), group=groups[0], ans=a)

urls = ["https://i0.wp.com/images-prod.healthline.com/hlcmsresource/images/AN_images/healthy-eating-ingredients-1296x728-header.jpg?w=1155&h=1528",
        "https://i.ndtvimg.com/i/2016-06/chinese-625_625x350_81466064119.jpg",
        "https://cdn.citynomads.com/wp-content/uploads/2017/06/08154455/straits-kitchen-cover3.png",
        "https://i.ndtvimg.com/i/2016-06/chinese-625_625x350_81466064119.jpg",
        "https://media.timeout.com/images/105370171/630/472/image.jpg"]
for url in urls:
    # import ssl
    # ssl._create_default_https_context = ssl._create_unverified_context
    # img = Image.open(urlopen(url))
    # import base64
    # image_file = base64.b64encode(img.tobytes())
    data = ImageData.create(group=groups[0], url=url)
    for j in range(5):
        ImageLabel.objects.update_or_create(image=data, label="food{}".format(j))

users = CustomUser.objects.filter(is_active=True, is_approved=True, is_admin=False)
print("validating: {}, voting: {}, user: {}".format(len(validating_qns), len(voting_qas), len(users)))
assign(users, Assignment, ValidatingData.objects.all(), Data, NUM_USER_PER_TASK=3)
assign(users, Assignment, VotingData.objects.filter(is_active=True), Data, NUM_USER_PER_TASK=5)
assign(users, Assignment, FinalizedData.objects.all(), Data, NUM_USER_PER_TASK=3)
assign(users, Assignment, ImageData.objects.all(), Data, NUM_USER_PER_TASK=3)