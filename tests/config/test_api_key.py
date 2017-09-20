import unittest
from os import environ as env
from zaifbot.config import get_keys, set_keys


class TestConfig(unittest.TestCase):
    def setUp(self):
        self._key = 'key'
        self._secret = 'secret'

    def test_set_keys(self):
        set_keys(self._key, self._secret)

        from_env = (env['ZAIFBOT_KEY'], env['ZAIFBOT_SECRET'])
        self.assertEqual(from_env, (self._key, self._secret))

    def test_get_keys_from_env(self):
        set_keys(self._key, self._secret)
        self.assertEqual(get_keys(), (self._key, self._secret))

    # todo: test from config file


if __name__ == '__main__':
    unittest.main()
