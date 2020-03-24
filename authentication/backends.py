import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class CustomBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            logging.getLogger("error_logger").error("user with account %s does not exists " % username)
            return None
        else:
            if user.check_password(password):
                return user
        return None
