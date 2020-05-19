from django.urls import reverse
from django.utils import translation
from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium_tests.webdriver import CustomChromeWebDriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.support.ui import Select
from authentication.models import CustomUser
from assign.models import Assignment

import time

class PageAdmin(StaticLiveServerTestCase):
    fixtures = ['fixtures.json']
    email = 'kkhadmin@gmail.com'
    pwd = 'kkhadmin!s123'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        translation.activate(settings.LANGUAGE_CODE)

        options = ChromeOptions()
        options.add_argument('--lang={}'.format(settings.LANGUAGE_CODE))
        options.add_argument('--no-sandbox')
        options.add_argument('--headless')
        options.add_argument('--disable-dev-shm-usage')
        cls.wd = CustomChromeWebDriver(chrome_options=options, live_server_url=cls.live_server_url)
        cls.wd.set_page_load_timeout(120)

    def setUp(self) -> None:
        self.wd.open(reverse('login'))
        self.wd.find_name('username').send_keys(self.email)
        self.wd.find_name("password").send_keys(self.pwd)
        self.wd.find_name("login").click()

    @classmethod
    def tearDownClass(cls):
        cls.wd.quit()
        super().tearDownClass()

    def test_user_list_approve(self):
        self.wd.open(reverse('modify_users'))

        pending_trs = self.wd.find_name('pending').find_element_by_tag_name('tbody').find_elements_by_tag_name('tr')
        approved_trs = self.wd.find_name('approved').find_element_by_tag_name('tbody').find_elements_by_tag_name('tr')
        first_tr = pending_trs[0]
        email = first_tr.find_element_by_name('email').text
        first_tr.find_element_by_name('approve').click()

        self.assertTrue(CustomUser.objects.get(email=email).is_approved)
        self.assertEqual(len(pending_trs) - 1, len(
            self.wd.find_name('pending').find_element_by_tag_name('tbody').find_elements_by_tag_name('tr')))
        self.assertEqual(len(approved_trs) + 1, len(
            self.wd.find_name('approved').find_element_by_tag_name('tbody').find_elements_by_tag_name('tr')))

    def test_user_list_reject(self):
        self.wd.open(reverse('modify_users'))

        pending_trs = self.wd.find_name('pending').find_element_by_tag_name('tbody').find_elements_by_tag_name('tr')
        approved_trs = self.wd.find_name('approved').find_element_by_tag_name('tbody').find_elements_by_tag_name('tr')
        first_tr = pending_trs[0]
        email = first_tr.find_element_by_name('email').text
        first_tr.find_element_by_name('reject').click()

        self.assertFalse(CustomUser.objects.get(email=email).is_approved)
        self.assertEqual(len(pending_trs) - 1, len(
            self.wd.find_name('pending').find_element_by_tag_name('tbody').find_elements_by_tag_name('tr')))
        self.assertEqual(len(approved_trs), len(
            self.wd.find_name('approved').find_element_by_tag_name('tbody').find_elements_by_tag_name('tr')))

    def test_user_list_approved(self):
        self.wd.open(reverse('modify_users'))

        approved_trs = self.wd.find_name('approved').find_element_by_tag_name('tbody').find_elements_by_tag_name('tr')
        active_tr_ids = []
        inactive_tr_ids = []
        for i, tr in enumerate(approved_trs):
            email = tr.find_element_by_name('email').text
            user = CustomUser.objects.get(email=email)
            if user.is_active:
                active_tr_ids.append(i)
            else:
                inactive_tr_ids.append(i)

        this_id = inactive_tr_ids[0]
        tr = self.wd.find_name('approved').find_element_by_tag_name('tbody') \
            .find_elements_by_tag_name('tr')[this_id]
        email = tr.find_element_by_name('email').text
        tr.find_element_by_name('activate').click()
        self.assertTrue(CustomUser.objects.get(email=email).is_active)

        new_tr = self.wd.find_name('approved').find_element_by_tag_name('tbody') \
            .find_elements_by_tag_name('tr')[this_id]
        self.assertTrue(new_tr.find_element_by_name('deactivate').is_enabled())
        self.assertFalse(new_tr.find_element_by_name('activate').is_enabled())

        this_id = active_tr_ids[0]
        tr = self.wd.find_name('approved').find_element_by_tag_name('tbody') \
            .find_elements_by_tag_name('tr')[this_id]
        email = tr.find_element_by_name('email').text
        tr.find_element_by_name('deactivate').click()
        self.assertFalse(CustomUser.objects.get(email=email).is_active)

        new_tr = self.wd.find_name('approved').find_element_by_tag_name('tbody') \
            .find_elements_by_tag_name('tr')[this_id]
        self.assertFalse(new_tr.find_element_by_name('deactivate').is_enabled())
        self.assertTrue(new_tr.find_element_by_name('activate').is_enabled())

    def test_dataset(self):
        self.wd.open(reverse('dataset'))

        self.wd.find_id('download_btn').click()
        # TODO

    def test_assign_contro_data_single(self):
        self.wd.open(reverse('update'))
        group = CustomUser.objects.get(email=self.email).group
        tasker = CustomUser.objects.filter(group=group, is_active=True, is_approved=True, is_admin=False).last()

        tr = self.wd.find_element_by_tag_name('tbody').find_elements_by_tag_name('tr')[0]
        qid = tr.find_element_by_tag_name('th').text

        self.assertFalse(Assignment.objects.filter(tasker=tasker, task=int(qid)))

        tr.find_element_by_name('assign_single').click()
        time.sleep(1)
        select = Select(self.wd.find_id('opt'))
        select.select_by_value(str(tasker.id))
        self.wd.find_name('assign').click()

        self.assertTrue(Assignment.objects.filter(tasker=tasker, task=int(qid)))

    def test_assign_contro_data_multiple(self):
        self.wd.open(reverse('update'))
        group = CustomUser.objects.get(email=self.email).group
        tasker = CustomUser.objects.filter(group=group, is_active=True, is_approved=True, is_admin=False).last()

        trs = self.wd.find_element_by_tag_name('tbody').find_elements_by_tag_name('tr')
        qids = []
        for tr in trs[:int(len(trs) / 2)]:
            tr.find_element_by_name('checked_task').click()
            qids.append(int(tr.find_element_by_tag_name('th').text))

        for qid in qids:
            self.assertFalse(Assignment.objects.filter(tasker=tasker, task=qid))

        self.wd.find_name('assign_multi').click()
        time.sleep(1)
        select = Select(self.wd.find_id('opt'))
        select.select_by_value(str(tasker.id))
        self.wd.find_name('assign').click()

        for qid in qids:
            self.assertTrue(Assignment.objects.filter(tasker=tasker, task=qid))

    def test_report(self):
        self.wd.open(reverse('report'))

        self.wd.find_id('download_btn').click()
        # TODO

    def test_admin_log(self):
        self.wd.open(reverse('log'))
        # TODO