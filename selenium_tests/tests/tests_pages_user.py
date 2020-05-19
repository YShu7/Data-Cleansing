from django.urls import reverse
from django.utils import translation
from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium_tests.webdriver import CustomChromeWebDriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.keys import Keys
from authentication.models import CustomUser
from pages.models.validate import ValidatingData
from pages.models.vote import VotingData, Choice
from pages.models.image import ImageData, ImageLabel
from pages.models.models import FinalizedData

import time


class PageUser(StaticLiveServerTestCase):
    fixtures = ['fixtures.json']
    email = 'kkhuser@gmail.com'
    pwd = 'kkhuser!s123'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        translation.activate(settings.LANGUAGE_CODE)

        options = ChromeOptions()
        options.add_argument('--lang={}'.format(settings.LANGUAGE_CODE))
        options.add_argument('--no-sandbox')
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

    def test_validate_approve(self):
        self.wd.open(reverse('tasks/validate'))
        done, curr, qid, vote, page_no = self._get_validate_info()

        self._click_approve(qid)
        self.wd.find_name('submit').click()

        self.assertIsNotNone(self.wd.find_class('alert-success'))

        curr_done = int(self.wd.find_name("done_progress").text.split(' ')[0])
        self._check_progress_bar(expected_done_progress=done + 1, expected_page_no=curr_done + 1, expected_curr_progress=0)

        self.assertEqual(vote['approved'] + 1, ValidatingData.objects.get(id=qid).num_approved)

    def test_validate_disapprove(self):
        self.wd.open(reverse('tasks/validate'))
        done, curr, qid, vote, page_no = self._get_validate_info()

        self._click_disapprove(qid, 'new answer')
        self.wd.find_name('submit').click()

        curr_done = int(self.wd.find_name("done_progress").text.split(' ')[0])
        self.assertIsNotNone(self.wd.find_class('alert-success'))
        self._check_progress_bar(expected_done_progress=done + 1, expected_page_no=curr_done + 1, expected_curr_progress=0)

        self.assertEqual(vote['disapproved'] + 1, ValidatingData.objects.get(id=qid).num_disapproved)
        self.assertIn('new answer', [c.answer for c in VotingData.objects.get(id=qid).choice_set.all()])

    def test_validate_combine(self):
        self.wd.open(reverse('tasks/validate'))
        modified_data = {}

        done, curr, qid, vote, page_no = self._get_validate_info()
        self._click_disapprove(qid, 'new answer')
        self._next_page()
        modified_data[qid] = {
            'approved': vote['approved'],
            'disapproved': vote['disapproved'] + 1,
            'new_ans': 'new answer',
        }

        self._check_progress_bar(expected_done_progress=done, expected_page_no=page_no + 1, expected_curr_progress=curr + 1)
        self.assertEqual(vote['disapproved'], ValidatingData.objects.get(id=qid).num_disapproved)

        try:
            voting_data = VotingData.objects.get(id=qid)
            self.assertNotIn('new answer', [c.answer for c in voting_data.choice_set.all()])
        except VotingData.DoesNotExist:
            pass

        done, curr, qid, vote, page_no = self._get_validate_info()
        self._click_approve(qid)
        self._next_page()
        modified_data[qid] = {
            'approved': vote['approved'] + 1,
            'disapproved': vote['disapproved'],
        }

        self._check_progress_bar(expected_done_progress=done, expected_page_no=page_no + 1, expected_curr_progress=curr + 1)
        self.assertEqual(vote['approved'], ValidatingData.objects.get(id=qid).num_approved)

        done, curr, qid, vote, page_no = self._get_validate_info()
        self._click_approve(qid)
        self._next_page()
        modified_data[qid] = {
            'approved': vote['approved'] + 1,
            'disapproved': vote['disapproved'],
        }

        self.wd.find_name('submit').click()

        self.assertIsNotNone(self.wd.find_class('alert-success'))
        self._check_progress_bar(expected_done_progress=done + 3, expected_page_no=page_no + 1, expected_curr_progress=0)
        for qid in modified_data:
            self.assertEqual(modified_data[qid]['approved'], ValidatingData.objects.get(id=qid).num_approved)
            self.assertEqual(modified_data[qid]['disapproved'], ValidatingData.objects.get(id=qid).num_disapproved)
            if 'new_ans' in modified_data[qid]:
                self.assertIn('new answer', [c.answer for c in VotingData.objects.get(id=qid).choice_set.all()])

    def test_vote(self):
        self.wd.open(reverse('tasks/vote'))

        done, qid, page_no, max_page_no = self._get_info()
        choice = VotingData.objects.get(id=qid).choice_set.all()[0]
        num_votes = Choice.objects.get(id=choice.id).num_votes

        self.wd.find_id('ans_{}'.format(choice.id)).click()
        self.wd.find_name('submit').click()

        self.assertEqual(num_votes + 1, Choice.objects.get(id=choice.id).num_votes)
        self._check_progress_bar(expected_done_progress=done + 1, expected_page_no=min(max_page_no, page_no + 1), expected_curr_progress=0)

    def test_keywords(self):
        self.wd.open(reverse('tasks/keywords'))

        done, qid, page_no, max_page_no = self._get_info()

        # TODO

    def test_image(self):
        self.wd.open(reverse('tasks/image'))

        done, qid, page_no, max_page_no = self._get_info()

        label_ele = self.wd.find_name('select_label')[2]
        label_id = int(label_ele.get_attribute('value'))
        label = ImageData.objects.get(id=qid).imagelabel_set.all().get(id=label_id)
        label_ele.click()
        time.sleep(1)
        # ensure the label is of the image data

        self.assertEqual(label.num_votes + 1, ImageLabel.objects.get(id=label.id).num_votes)
        self._check_progress_bar(expected_done_progress=done + 1, expected_page_no=min(max_page_no, page_no + 1),
                                 expected_curr_progress=0)

    def test_contro(self):
        self.wd.open(reverse('tasks/contro'))

        done, qid, page_no, max_page_no = self._get_info()

        choice = VotingData.objects.get(id=qid).choice_set.all()[0]

        self.wd.find_id('choice_{}'.format(choice.id)).click()
        self.wd.find_name('submit').click()
        time.sleep(1)

        self.assertFalse(VotingData.objects.filter(id=qid).exists())
        self.assertTrue(FinalizedData.objects.filter(id=qid).exists())
        self.assertEqual(choice.answer, FinalizedData.objects.get(id=qid).answer_text)
        self._check_progress_bar(expected_done_progress=0, expected_page_no=1,
                                 expected_curr_progress=0)

    def test_contro_new_ans(self):
        self.wd.open(reverse('tasks/contro'))

        done, qid, page_no, max_page_no = self._get_info()
        new_ans = "New Answer"

        self.wd.find_name('new_ans_btn').click()
        time.sleep(1)
        self.wd.find_id('new_ans_textarea').send_keys(new_ans)
        self.wd.find_id('update_btn').click()
        self.wd.find_name('submit').click()
        time.sleep(1)

        self.assertFalse(VotingData.objects.filter(id=qid).exists())
        self.assertTrue(FinalizedData.objects.filter(id=qid).exists())
        self.assertEqual(new_ans, FinalizedData.objects.get(id=qid).answer_text)
        self._check_progress_bar(expected_done_progress=0, expected_page_no=1,
                                 expected_curr_progress=0)

    def test_profile(self):
        self.wd.open(reverse('profile'))
        new_pwd = 'kkh!s123'

        self.wd.find_id('change_pwd').click()
        self.wd.find_name('old_password').send_keys(self.pwd)
        self.wd.find_name('new_password1').send_keys(new_pwd)
        self.wd.find_name('new_password2').send_keys(new_pwd)
        self.wd.find_name('confirm').click()

        self.assertTrue(CustomUser.objects.get(email=self.email).check_password(new_pwd))

    def test_profile_fail(self):
        self.wd.open(reverse('profile'))
        new_pwd = 'kkh!s123'
        old_pwd_ele = self.wd.find_name('old_password')
        new_pwd1_ele = self.wd.find_name('new_password1')
        new_pwd2_ele = self.wd.find_name('new_password2')

        self.wd.find_id('change_pwd').click()
        old_pwd_ele.send_keys('sk23100031')
        new_pwd1_ele.send_keys(new_pwd)
        new_pwd2_ele.send_keys(new_pwd)
        self.wd.find_name('confirm').click()
        time.sleep(1)

        self.assertTrue(CustomUser.objects.get(email=self.email).check_password(self.pwd))
        self.assertFalse(CustomUser.objects.get(email=self.email).check_password(new_pwd))

        old_pwd_ele = self.wd.find_name('old_password')
        new_pwd1_ele = self.wd.find_name('new_password1')
        new_pwd2_ele = self.wd.find_name('new_password2')
        old_pwd_ele.send_keys(Keys.CONTROL + 'a')
        old_pwd_ele.send_keys(Keys.DELETE)
        old_pwd_ele.send_keys(self.pwd)
        new_pwd1_ele.send_keys(Keys.CONTROL + 'a')
        new_pwd1_ele.send_keys(Keys.DELETE)
        new_pwd1_ele.send_keys(new_pwd)
        new_pwd2_ele.send_keys(Keys.CONTROL + 'a')
        new_pwd2_ele.send_keys(Keys.DELETE)
        new_pwd2_ele.send_keys(new_pwd + '1')

        self.assertTrue(CustomUser.objects.get(email=self.email).check_password(self.pwd))
        self.assertFalse(CustomUser.objects.get(email=self.email).check_password(new_pwd))

    def _get_info(self):
        done = int(self.wd.find_name("done_progress").text.split(' ')[0])
        qid = self.wd.find_tag('tbody').find_elements_by_tag_name('th')[0].text
        page_no = int(self.wd.find_name('page_no').text.split(' ')[0])
        max_page_no = int(self.wd.find_name('page_no').text.split(' ')[-1])

        return done, qid, page_no, max_page_no

    def _get_validate_info(self):
        done, qid, page_no, _ = self._get_info()
        if self.wd.find_name("curr_progress") is None:
            curr = 0
        else:
            curr = int(self.wd.find_name("curr_progress").text.split(' ')[0])
        vote = {
            'approved': ValidatingData.objects.get(id=qid).num_approved,
            'disapproved': ValidatingData.objects.get(id=qid).num_disapproved,
        }


        return done, curr, qid, vote, page_no

    def _click_approve(self, qid):
        self.wd.find_id('approve_{}'.format(qid)).click()
        time.sleep(1)

    def _click_disapprove(self, qid, new_ans):
        self.wd.implicitly_wait(10)
        self.wd.find_id('change_{}'.format(qid)).click()

        self.wd.implicitly_wait(10)
        ans_modal = self.wd.find_id('new_ans_textarea')
        ans_modal.send_keys(Keys.TAB)
        ans_modal.clear()
        ans_modal.send_keys(new_ans)
        self.wd.implicitly_wait(10)
        self.wd.find_id('update_btn').click()
        time.sleep(1)

    def _next_page(self):
        self.wd.find_link_text("next").click()

    def _check_progress_bar(self, expected_done_progress, expected_page_no, expected_curr_progress):
        self.assertEqual(expected_done_progress, int(self.wd.find_name("done_progress").text.split(' ')[0]))
        self.assertEqual(expected_page_no, int(self.wd.find_name('page_no').text.split(' ')[0]))
        if expected_curr_progress == 0:
            self.assertIsNone(self.wd.find_name("curr_progress"))
        else:
            self.assertEqual(expected_curr_progress, int(self.wd.find_name('curr_progress').text.split(' ')[0]))