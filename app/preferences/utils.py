import collections
import configparser
import os.path

from app import PREFERENCES_CONFIG_FILE


# NOTE(currently not used, since no settings use combo boxes now. keeping this just in case)
Choices = collections.namedtuple("Choices", ["default", "items"])
Choices.__doc__ = \
    """Represents the choices available for a specific combo box in the preferences dialog."""


class PreferencesConfig:
    """The class responsible for the interaction with the preferences config file.

    Attributes
    ----------
    _CONFIG_SECTION: str
        the name of the config section used for storing the preferences
    DEFAULTS: dict[str: str]
        the default values for every available option
    PREFERENCES: list[str]
        the valid setting keys (for subscripting instance)
    _filepath: str
        the path to the config file (will be created if it doesn't exist)
    _parser: configparser.ConfigParser
        the parser responsible for parsing self._filepath. initialized
        with interpolation=None to avoid the name template – which defaults
        to '%(title)s – %(uploader)s.%(ext)s' – from being interpolated if
        some variables in the string were to have the same name as the ones
        in the file.
    """

    _CONFIG_SECTION = "preferences"
    DEFAULTS = {
        "output_directory": "~/Downloads/YoutubeDL/",
        "name_template": "%(title)s – %(uploader)s.%(ext)s",
        "timeout": str(5),
        "check_certificate": str(True),
        "video_format_selector": "(bestvideo[ext=mp4][width=1920]/"
                                 "bestvideo[ext=mp4])+bestaudio[ext=m4a]/"
                                 "bestvideo+bestaudio/best[ext=mp4]/best",
        "audio_format_selector": "bestaudio[ext=mp3]/bestaudio"
    }
    PREFERENCES = list(DEFAULTS)

    def __init__(self, filepath=PREFERENCES_CONFIG_FILE):
        """Initialize the PreferencesConfig class.

        Parameters
        ----------
        filepath: str
            the path to the config file (will be created if it doesn't exist or if it is empty)

        Create the config file if necessary, load the preferences from it,
        if they are not valid, reset the config file.
        """
        self._filepath = filepath
        self._parser = configparser.ConfigParser(interpolation=None)
        self._parser.add_section(self._CONFIG_SECTION)
        if not os.path.exists(self._filepath):
            self.reset(save=True)
        with open(self._filepath, "r") as file:
            self._parser.read_file(file)
        if not self._parser_valid():
            self.reset(save=True)
        with open(self._filepath, "r") as file:
            self._parser.read_file(file)

    def _parser_valid(self):
        """Return wether or not the parser has all of the required preferences."""
        return not bool(set(self.PREFERENCES) - set(self._parser.options(self._CONFIG_SECTION)))

    def __getitem__(self, args):
        """Get a setting by subscript.

        Parameters
        ----------
        args: str or tuple
            the key of the setting or
            a tuple of the key and the type to coerce to: bool, int or float (default is str)

        Raises
        ------
        KeyError
            if the key is not a valid setting key
        TypeError
            if the type to coerce to is not available (see above)
        ValueError (raised by the self._parser.get* methods)
            if the string could not be coerced to the specified type

        Examples
        --------
        >>> config['check_certificate']
        'False'

        # specify type to cast to
        >>> config['check_certificate', bool]
        False
        """
        try:
            key, coerce = args
        except ValueError:  # can't unpack
            key, coerce = args, None

        if not self._parser.has_option(self._CONFIG_SECTION, key):
            raise KeyError(f"invalid setting key '{key}'")

        try:
            get = {
                bool: self._parser.getboolean,
                int: self._parser.getint,
                float: self._parser.getfloat,
                str: self._parser.get,
                None: self._parser.get
            }[coerce]
        except KeyError:
            raise TypeError(f"can't coerce to type '{coerce}'") from None

        return get(self._CONFIG_SECTION, key)

    def __setitem__(self, key, item):
        """Set a setting by subscript.

        Parameters
        ---------
        key: str
            the name of the setting to set
        item
            the item to assign to the requested setting. will be cast to a string

        Raises
        ------
        KeyError
            if 'key' is not a valid setting key

        Examples
        --------

        >>> self.config['output_directory'] = '~/output'
        >>> self.config['output_directory']
        '~/output'

        # save non string type int (bool and float also available)
        >>> self.config['timeout'] = 7
        >>> self.config['timeout']
        '7'
        >>> self.config['timeout', int]
        7
        """
        if not self._parser.has_option(self._CONFIG_SECTION, key):
            raise KeyError(f"invalid setting key '{key}'")

        self._parser.set(self._CONFIG_SECTION, key, str(item))

    def reset(self, save=False):
        """Reset the preferences config parser (and optionally save)."""
        for pref in self.DEFAULTS:
            self._parser.set(self._CONFIG_SECTION, pref, self.DEFAULTS[pref])
        if save:
            self.save()

    def save(self):
        """Write self._parser to self._filepath."""
        with open(self._filepath, "w") as file:
            self._parser.write(file)
