from django.urls import reverse
from django.utils import translation
from django.conf import settings
from selenium_tests.test import SeleniumTestCase
from selenium_tests.webdriver import CustomChromeWebDriver
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.support.ui import Select
from authentication.models import CustomUser, CustomGroup



class Auth(SeleniumTestCase):
    def setUp(self):
        translation.activate(settings.LANGUAGE_CODE)

        self.group = CustomGroup.objects.create(name="TestGroup")
        self.user = CustomUser.objects.create_user(
            email="user@gmail.com", username="user", password="user",
            certificate="G1111111M", group=self.group)
        options = ChromeOptions()
        options.add_argument('--lang={}'.format(settings.LANGUAGE_CODE))
        self.wd = CustomChromeWebDriver(chrome_options=options)

    def tearDown(self):
        self.wd.quit()

    def test_login(self):
        self.login("user@gmail.com", 'user')
        self.assertEqual(self.wd.find_class("navbar-text").text, "Welcome, {}".format(self.user.username))

    def test_login_fail(self):
        self.login("user@gmail.com", 'incorrect_pwd')
        self.assertIsNotNone(self.wd.find_class('alert-danger'))

    def test_login_to_signup(self):
        self.open(reverse('login'))

        self.wd.find_name('signup').click()
        self.assertEqual(self.wd.find_class('card-header').text, "User Registration")

    def test_signup(self):
        self.signup("new", 'G12342313M', 'new@gmail.com', 'newpwd123()*', 'newpwd123()*', self.group.id)
        self.assertIsNotNone(CustomUser.objects.filter(
            username='new', email='new@gmail.com', certificate='G12342313M').first())

    def test_signup_fail(self):
        self.open(reverse('signup'))
        self.signup("new", 'G12342313M', 'new@gmail.com', 'newpwd123()*', 'diffpwd123()*', self.group.id)
        self.assertIsNone(CustomUser.objects.filter(
            username='new', email='new@gmail.com', certificate='G12342313M').first())

    def test_pwd_reset(self):
        self.open(reverse('password_reset'))
        self.wd.find_name('email').send_keys('user@gmail.com')

        self.assertIsNotNone(self.wd.find_name('sent_confirm'))
        self.assertIsNotNone(self.wd.find_name('check_request'))

    def test_pwd_reset_fail(self):
        self.open(reverse('password_reset'))
        self.wd.find_name('email').send_keys('nonexist@gmail.com')

        self.assertIsNotNone(self.wd.find_class('alert-danger'))

    def test_pwd_change(self):
        new_pwd = 'new034I!8032'
        self.pwd_change('user', new_pwd, new_pwd)

        self.assertEqual(self.user.password, new_pwd)

    def test_pwd_change_fail(self):
        self.pwd_change('user', 'new034I!8032', 'new0f!8032')

        self.assertEqual(self.user.password, 'user')

    def login(self, username, pwd):
        """
        Helper function for login page.
        :param username: input for username
        :param pwd: input for password
        """
        self.open(reverse('login'))

        self.wd.find_name('username').send_keys(username)
        self.wd.find_name("password").send_keys(pwd)
        self.wd.find_name("login").click()

    def signup(self, username, certificate, email, pwd1, pwd2, gid):
        self.open(reverse('signup'))

        self.wd.find_name('username').send_keys(username)
        self.wd.find_name('certificate').send_keys(certificate)
        self.wd.find_name('email').send_keys(email)
        self.wd.find_name('password1').send_keys(pwd1)
        self.wd.find_name('password2').send_keys(pwd2)
        select = Select(self.wd.find_name('group'))
        select.select_by_value(str(gid))

        self.wd.find_name('signup').click()

    def pwd_change(self, old_pwd, pwd1, pwd2):
        self.open(reverse('password_change'))

        self.wd.find_name('old_password').send_keys(old_pwd)
        self.wd.find_name('new_password1').send_keys(pwd1)
        self.wd.find_name('new_password2').send_keys(pwd2)

        self.wd.find_id('update_pwd').click()