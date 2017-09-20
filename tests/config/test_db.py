import unittest
from zaifbot.config.db import get_database_url
from zaifbot.config.handler import ConfigFileHandler
import tempfile
import os
from unittest.mock import Mock


class TestDBConfig(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mktemp()
        self.config_file = os.path.join(self.temp_dir, 'config_file')
        self.config = ConfigFileHandler(path=self.config_file)

    def test_url_path(self):
        test_db = os.path.join(self.temp_dir, 'test_db')
        test_engine = {
            'db': {
                'drivername': 'sqlite',
                'database': test_db,
            },
        }

        self.config.read_by_section = Mock(return_value=test_engine['db'])
        url = str(get_database_url(self.config)).replace("\\", "/")
        right_one = 'sqlite:///' + os.path.normpath(os.path.join(self.temp_dir, 'test_db')).replace("\\", "/")
        self.assertEqual(url, right_one)

if __name__ == '__main__':
    unittest.main()
