from setuptools import setup, find_packages
from zaifbot import install_ta_lib

install_ta_lib()

setup(
    name='zaifbot',
    version='0.0.4',
    description='Zaif Bot Library',
    long_description='https://pypi.python.org/pypi/zaifbot',
    url='https://github.com/techbureau/zaifbot',
    author='AkiraTaniguchi DaikiShiroi Monji',
    author_email='a.taniguchi@techbureau.jp daikishiroi@gmail.com',
    packages=find_packages(),
    license='MIT',
    keywords='zaif bit coin btc xem mona jpy virtual currency block chain bot',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License'
    ],
    install_requires=[
        'zaifapi>=1.5.3',
        'numpy',
        'pandas',
        'SQLAlchemy',
        'websocket-client',
        'slackclient',
        'pytz',
        'slack_logger',
        'TA-Lib==0.4.10',
    ],
    entry_points="""\
      [console_scripts]
      init_database = zaifbot.setup:init_database
      install_ta_lib = zaifbot:install_ta_lib
      """,
)
