from setuptools import setup, find_packages
from zaifbot import __version__


def readme():
    with open('README.rst', encoding='utf-8') as f:
        return f.read()

setup(
    name='zaifbot',
    version=__version__,
    description='trading bot framework for zaif exchange',
    long_description=readme(),
    url='https://github.com/techbureau/zaifbot',
    author='AkiraTaniguchi DaikiShiroi Monji',
    author_email='a.taniguchi@techbureau.jp daikishiroi@gmail.com',
    include_package_data=True,
    packages=find_packages(),
    license='MIT',
    keywords='zaif bit coin btc xem mona jpy virtual currency block chain bot',
    classifiers=[
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License'
    ],
    install_requires=[
        'SQLAlchemy',
        'slackclient',
        'slack_logger',
        'zaifapi',
        'numpy',
        'pandas',
        'flask',
    ],
    extras_require={
        'ta-lib': ['TA-Lib']
    },
    entry_points="""\
      [console_scripts]
      init_database = zaifbot.db.seed:init_database
      clear_database = zaifbot.db.seed:clear_database
      refresh_database = zaifbot.db.seed:refresh_database
      install_ta_lib = zaifbot.setup.talib:install_ta_lib
      """,
)
