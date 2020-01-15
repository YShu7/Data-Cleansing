from django.test import TestCase
from django.http.request import HttpRequest
from django.contrib.auth import get_user_model, authenticate
import django
django.setup()

from .views import signup
from .backends import CustomBackend


class SignUpTestCase(TestCase):
    def test_signup(self):
        request = HttpRequest()
        email = 'test@gmail.com'
        pwd = 'guy123123'

        try:
            user = get_user_model().objects.get(email=email)
            user.delete()
        except Exception:
            pass

        request.method = "POST"
        request.session = []
        request.POST = {
            'username': 'test',
            'certificate': 'G12312312',
            'email': email,
            'password1': pwd,
            'password2': pwd,
            'group': '331'
        }

        response = signup(request)

        try:
            get_user_model().objects.get(email=email)
        except Exception:
            raise Exception(response.request)

        user = CustomBackend().authenticate(request, username=email, password=pwd)
        if not user:
            raise Exception("Username and password don't match.")