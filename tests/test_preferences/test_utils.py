import configparser
import random
import secrets
import tempfile
import unittest

from app.preferences.utils import PreferencesConfig


class TestPreferencesConfig(unittest.TestCase):
    """Test the PreferencesConfig class, which is responsible of the preferences config file.

    Attributes
    ----------
    temp_file: tempfile.NamedTemporaryFile
        a temporary file used for testing
        will be deleted as soon as the reference to it is lost
    config: PreferencesConfig
        the config object we are testing
    """

    def setUp(self):
        """Set up the necessary attributes."""
        self.temp_file = tempfile.NamedTemporaryFile(mode="w+")
        self.config = PreferencesConfig(self.temp_file.name)

    def test_init(self):
        """Verify the correct initialization of the PreferencesConfig object."""
        self.assertTrue(self.config._parser.has_section(self.config._CONFIG_SECTION))
        # TODO(add more checks)

    def test_reset(self):
        """Test the 'reset' method."""
        for pref in self.config.PREFERENCES:
            self.config[pref] = secrets.token_hex(4)

        self.config.reset()
        for pref in self.config.PREFERENCES:
            self.assertEqual(self.config[pref], self.config.DEFAULTS[pref])

    def test_subscript(self):
        """Test the __setitem__ and __getitem__ magic methods."""
        for pref in self.config.PREFERENCES:
            v = secrets.token_hex(4)
            self.config[pref] = v
            self.assertEqual(self.config[pref], v)

        fake = ["hello", "this", "is", "a", "test"]
        for pref in fake:
            with self.assertRaises(KeyError):
                self.config[pref] = ""

            with self.assertRaises(KeyError):
                self.config[pref]

        self.config['timeout'] = 8
        self.assertIsInstance(self.config['timeout'], str)
        self.assertIsInstance(self.config['timeout', int], int)

        self.config['private_mode'] = True
        self.assertIsInstance(self.config['private_mode'], str)
        self.assertIsInstance(self.config['private_mode', bool], bool)

        with self.assertRaises(TypeError):
            self.config['geo_bypass', list]

        with self.assertRaises(ValueError):
            self.config['private_mode', int]

    def test_save(self):
        """Test the 'save' method."""
        test_prefs = {}
        for pref in self.config.PREFERENCES:
            v = random.choice([secrets.token_hex(4), self.config.DEFAULTS[pref]])
            self.config[pref] = v
            test_prefs[pref] = v

        self.config.save()
        parser = configparser.ConfigParser(interpolation=None)
        with open(self.temp_file.name, "r") as file:
            parser.read_file(file)

        for pref in test_prefs:
            self.assertEqual(parser[self.config._CONFIG_SECTION][pref], test_prefs[pref])
