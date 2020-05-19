from django.urls import reverse
from django.utils import translation
from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver import ChromeOptions
from selenium_tests.webdriver import CustomChromeWebDriver
from selenium.webdriver.support.ui import Select
from authentication.models import CustomUser, CustomGroup


class Auth(StaticLiveServerTestCase):
    fixtures = ['fixtures.json']
    email = 'kkhuser@gmail.com'
    pwd = 'kkhuser!s123'
    group = CustomUser.objects.get(email=email).group
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        translation.activate(settings.LANGUAGE_CODE)

        options = ChromeOptions()
        options.add_argument('--lang={}'.format(settings.LANGUAGE_CODE))
        options.add_argument('--no-sandbox')
        cls.wd = CustomChromeWebDriver(chrome_options=options, live_server_url=cls.live_server_url)
        cls.wd.set_page_load_timeout(120)

    @classmethod
    def tearDownClass(cls):
        cls.wd.quit()
        super().tearDownClass()

    def test_login(self):
        user = CustomUser.objects.get(email=self.email)
        self.login(self.email, self.pwd)
        self.assertEqual(self.wd.find_class("navbar-text").text.split(',')[1].strip(), user.username)

    def test_login_fail(self):
        self.login(self.email, 'incorrect_pwd')
        self.assertIsNotNone(self.wd.find_class('alert-danger'))

    def test_login_to_signup(self):
        self.wd.open(reverse('login'))

        self.wd.find_name('signup').click()
        self.assertEqual(self.wd.find_class('card-header').text, "User Registration")

    def test_signup(self):
        self.signup("new", 'G12342313M', 'new@gmail.com', 'newpwd123()*', 'newpwd123()*', self.group.id)
        self.assertIsNotNone(CustomUser.objects.filter(
            username='new', email='new@gmail.com', certificate='G12342313M').first())

    def test_signup_fail(self):
        self.wd.open(reverse('signup'))
        self.signup("new", 'G12342313M', 'new@gmail.com', 'newpwd123()*', 'diffpwd123()*', self.group.id)
        self.assertIsNone(CustomUser.objects.filter(
            username='new', email='new@gmail.com', certificate='G12342313M').first())

    def test_pwd_reset(self):
        self.wd.open(reverse('password_reset'))
        self.wd.find_name('email').send_keys(self.email)
        self.wd.find_name('submit').click()

        self.assertIsNotNone(self.wd.find_name('sent_confirm'))
        self.assertIsNotNone(self.wd.find_name('check_request'))

    def test_pwd_reset_fail(self):
        self.wd.open(reverse('password_reset'))
        self.wd.find_name('email').send_keys('nonexist@gmail.com')
        self.wd.find_name('submit').click()

        self.assertIsNotNone(self.wd.find_class('alert-danger'))

    def test_pwd_change(self):
        new_pwd = 'new034I!8032'
        self.pwd_change(new_pwd, new_pwd)

        self.assertTrue(CustomUser.objects.get(email=self.email).check_password(new_pwd))

    def test_pwd_change_fail(self):
        self.pwd_change('new034I!8032', 'new0f!8032')

        self.assertTrue(CustomUser.objects.get(email=self.email).check_password(self.pwd))

    def login(self, username, pwd):
        """
        Helper function for login page.
        :param username: input for username
        :param pwd: input for password
        """
        self.wd.open(reverse('login'))

        self.wd.find_name('username').send_keys(username)
        self.wd.find_name("password").send_keys(pwd)
        self.wd.find_name("login").click()

    def signup(self, username, certificate, email, pwd1, pwd2, gid):
        self.wd.open(reverse('signup'))

        self.wd.find_name('username').send_keys(username)
        self.wd.find_name('certificate').send_keys(certificate)
        self.wd.find_name('email').send_keys(email)
        self.wd.find_name('password1').send_keys(pwd1)
        self.wd.find_name('password2').send_keys(pwd2)
        select = Select(self.wd.find_name('group'))
        select.select_by_value(str(gid))

        self.wd.find_name('signup').click()

    def pwd_change(self, pwd1, pwd2):
        self.login(self.email, self.pwd)

        self.wd.open(reverse('profile'))

        self.wd.find_id('change_pwd').click()

        self.wd.find_name('old_password').send_keys(self.pwd)
        self.wd.find_name('new_password1').send_keys(pwd1)
        self.wd.find_name('new_password2').send_keys(pwd2)

        self.wd.find_name('confirm').click()