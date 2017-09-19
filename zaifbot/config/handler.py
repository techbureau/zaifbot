import os
import configparser


def _get_config():
    config = configparser.ConfigParser()
    return config


class ConfigFileHandler:
    default_path = os.path.join(os.path.expanduser('~'), '.zaifbot')

    def __init__(self, *args, **kwargs):
        self._path = kwargs.get('path') or self.default_path

    def read_by_section(self, section):
        config = _get_config()
        config.read(self._path)

        results = {}
        try:
            for key in config.options(section):
                results[key] = config[section][key]
            return results
        except configparser.NoSectionError:
            return None

    def read_by_section_and_key(self, section, key):
        config = _get_config()
        config.read(self._path)

        try:
            return config[section][key]
        except (configparser.NoSectionError, KeyError):
            return None

    def set_config(self, section, key, value):
        config = _get_config()
        config.read(self._path)

        if section not in config.sections():
            config.add_section(section)
        config.set(section, key, value)

        with open(self._path, 'w') as configfile:
            config.write(configfile)
