from setuptools import setup, find_packages

setup(
    name='zaifbot',
    version='0.0.3',
    description='Zaif Bot Library',
    long_description='https://pypi.python.org/pypi/zaifbot',
    url='https://github.com/Akira-Taniguchi/zaifbot',
    author='AkiraTaniguchi Monji',
    author_email='a.taniguchi@techbureau.jp ttskmnj@gmail.com',
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
        'zaifapi==1.5.2',
        'numpy==1.12.0',
        'pandas==0.20.1',
        'reportlab==3.4.0',
        'SQLAlchemy==1.1.5',
        'websocket-client==0.40.0',
        'slackclient==1.0.5',
        'plotly==2.0.8',
        'pytz==2017.2'
    ],
    entry_points="""\
      [console_scripts]
      update_assignee_id = zaifbot:main
      init_database = zaifbot.modules.dao:init_database
      """,
    include_package_data=True
)
