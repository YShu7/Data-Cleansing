from django.utils import timezone
from django.contrib.auth import get_user_model

from .models import Log


def get_group_report(group):
    members = get_user_model().objects.filter(group=group, is_approved=True, is_active=True)
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
    if group is None:
        return get_user_model().objects.filter(is_approved=None, is_superuser=False).order_by('date_joined')
    else:
        return get_user_model().objects.filter(is_approved=None, group=group, is_superuser=False, is_admin=False).order_by(
            'date_joined')


def get_approved_users(group=None):
    if group is None:
        return get_user_model().objects.filter(is_approved=True, is_superuser=False).order_by(
            'date_joined')
    else:
        return get_user_model().objects.filter(is_approved=True, group=group, is_superuser=False,
                                               is_admin=False).order_by(
            'date_joined')


def get_log_msg(log):
    return {
        "logger": "{}({})".format(log.admin.username, log.admin.certificate),
        "timestamp": log.timestamp,
        "msg": "{} {}({})".format(log.get_action_display(), log.account.username, log.account.certificate),
        "extra": log.extra_msg,
    }


def log(admin, action, account, msg=""):
    Log.objects.update_or_create(admin=admin, action=action, account=account, extra_msg=msg, timestamp=timezone.now())
