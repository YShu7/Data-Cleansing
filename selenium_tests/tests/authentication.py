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
        """
        Django Admin login test
        """
        self.open(reverse('login'))

        self.wd.find_name('username').send_keys("user@gmail.com")
        self.wd.find_name("password").send_keys('user')
        self.wd.find_name("login").click()

        self.assertEqual(self.wd.find_class("navbar-text").text, "Welcome, {}".format(self.user.username))

    def test_login_signup(self):
        self.open(reverse('login'))

        self.wd.find_name('signup').click()
        self.assertEqual(self.wd.find_class('card-header').text, "User Registration")

    def test_signup(self):
        self.open(reverse('signup'))

        self.wd.find_name('username').send_keys("new")
        self.wd.find_name('certificate').send_keys('G12342313M')
        self.wd.find_name('email').send_keys('new@gmail.com')
        self.wd.find_name('password1').send_keys('newpwd123()*')
        self.wd.find_name('password2').send_keys('newpwd123()*')
        select = Select(self.wd.find_name('group'))
        select.select_by_value(str(self.group.id))

        self.wd.find_name('signup').click()

        self.assertIsNotNone(CustomUser.objects.filter(
            username='new', email='new@gmail.com', certificate='G12342313M').first())

    def test_signup_fail(self):
        self.open(reverse('signup'))

        self.wd.find_name('username').send_keys("new")
        self.wd.find_name('certificate').send_keys('G12342313M')
        self.wd.find_name('email').send_keys('new@gmail.com')
        self.wd.find_name('password1').send_keys('newpwd223()*')
        self.wd.find_name('password2').send_keys('newpwd123()*')
        select = Select(self.wd.find_name('group'))
        select.select_by_value(str(self.group.id))

        self.wd.find_name('signup').click()

        self.assertIsNone(CustomUser.objects.filter(
            username='new', email='new@gmail.com', certificate='G12342313M').first())