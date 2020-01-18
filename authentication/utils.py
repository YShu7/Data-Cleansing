from django.contrib.auth import update_session_auth_hash, get_user_model


def get_group_report(group):
    members = get_user_model().objects.filter(group=group)
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


def get_pending_users(group=None):
    if not group:
        return get_user_model().objects.filter(is_approved=False)
    return get_user_model().objects.filter(is_approved=False, group=group).order_by('date_joined')


def get_approved_users(group=None):
    if not group:
        return get_user_model().objects.filter(is_approved=True)
    return get_user_model().objects.filter(is_approved=True, group=group).order_by('date_joined')