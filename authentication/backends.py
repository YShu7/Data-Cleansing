from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from .models import CustomUser
from django.contrib.auth.backends import ModelBackend
import logging

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

    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(pk=user_id)
            if user.is_active:
                return user
            else:
                return None
        except User.DoesNotExist:
            return None