from .models import *


def get_group_report(group):
    members = CustomUser.objects.filter(group=group)
    num_ans = 0
    corr_num_ans = 0
    point = 0
    for member in members:
        num_ans += member.num_ans
        corr_num_ans += member.correct_num_ans
        point += member.point
    if num_ans == 0:
        accuracy = 1
    else:
        accuracy = corr_num_ans / num_ans
    return {"num_ans": num_ans, "point": point, "accuracy": accuracy}