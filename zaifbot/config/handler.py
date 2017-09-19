import os
import configparser


def _only_file_exists(func):
    def _inner(self, *args, **kwargs):
        if os.path.isfile(self._path):
            return func(self, *args, **kwargs)
    return _inner


class ConfigFileHandler:
    default_path = os.path.join(os.path.expanduser('~'), '.zaifbot')

    def __init__(self, *args, **kwargs):
        self._path = kwargs.get('path') or self.default_path

    @_only_file_exists
    def read_by_section(self, section):
        config = self._get_config()

        results = {}
        try:
            for key in config.options(section):
                results[key] = config[section][key]
            return results
        except configparser.NoSectionError:
            return None

    @_only_file_exists
    def read_by_section_and_key(self, section, key):
        config = self._get_config()

        try:
            return config[section][key]
        except (configparser.NoSectionError, KeyError):
            return None

    @_only_file_exists
    def set_config(self, section, key, value):
        config = self._get_config()
        if section not in config.sections():
            config.add_section(section)
        config.set(section, key, value)

        with open(self._path, 'w') as configfile:
            config.write(configfile)

    def _get_config(self):
        config = configparser.ConfigParser()
        config.read(self._path)
        return config
