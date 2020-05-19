from django.test import TestCase

from pages.templatetags.filter import split, remove_lang, get_lang


class FilterViewTestCase(TestCase):
    def test_split(self):
        str = 's t r'
        self.assertEqual(split(str), str.split())

        str = 's, t r'
        self.assertEqual(split(str, ','), str.split(','))

    def test_remove_lang(self):
        url = '/en-us/this/is/a/test'
        self.assertEqual(remove_lang(url), '/this/is/a/test')

    def test_get_lang(self):
        url = '/en-us/this/is/a/test'
        self.assertEqual(get_lang(url), 'en-us')