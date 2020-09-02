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

    def test_parser_valid(self):
        """Test the '_parser_valid' method."""
        self.assertTrue(self.config._parser_valid())  # should be valid initially

        add_options = [secrets.token_hex(4) for _ in range(5)]
        for option in add_options:  # add useless options
            self.config._parser.set(self.config._CONFIG_SECTION, option, secrets.token_hex(4))
        self.assertTrue(self.config._parser_valid())  # all required options are still here

        for option in self.config.PREFERENCES[:2]:  # remove options which are required
            self.config._parser.remove_option(self.config._CONFIG_SECTION, option)
        self.assertFalse(self.config._parser_valid())

        self.config._parser[self.config._CONFIG_SECTION].clear()  # clear options
        self.assertFalse(self.config._parser_valid())

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

        self.config['check_certificate'] = True
        self.assertIsInstance(self.config['check_certificate'], str)
        self.assertIsInstance(self.config['check_certificate', bool], bool)

        with self.assertRaises(TypeError):
            self.config['audio_format_selector', list]

        with self.assertRaises(ValueError):
            self.config['check_certificate', int]

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
