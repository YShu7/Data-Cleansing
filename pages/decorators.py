from django.contrib.auth.decorators import login_required, user_passes_test, REDIRECT_FIELD_NAME


def admin_login_required(function=login_required(), redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    actual_decorator = user_passes_test(
        lambda u: u.is_admin,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    return actual_decorator(function)


def user_login_required(function=login_required(), redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    actual_decorator = user_passes_test(
        lambda u: not u.is_admin and not u.is_superuser,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    return actual_decorator(function)