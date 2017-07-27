from setuptools import setup, find_packages
from zaifbot import install_ta_lib

install_ta_lib()


def readme():
    with open('README.rst') as f:
        return f.read()

setup(
    name='zaifbot',
    version='0.0.4',
    description='trading bot framework for zaif exchange',
    long_description='',
    url='https://github.com/techbureau/zaifbot',
    author='AkiraTaniguchi DaikiShiroi Monji',
    author_email='a.taniguchi@techbureau.jp daikishiroi@gmail.com',
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
        'zaifapi',
        'numpy',
        'pandas',
        'SQLAlchemy',
        'websocket-client',
        'slackclient',
        'pytz',
        'slack_logger',
        'TA-Lib',
    ],
    entry_points="""\
      [console_scripts]
      init_database = zaifbot.setup:init_database
      install_ta_lib = zaifbot:install_ta_lib
      """,
)
