from setuptools import setup, find_packages

setup(
    name='zaifbot',
    version='0.0.0.dev1',
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
<<<<<<< HEAD
    install_requires=['zaifapi==1.3.2', 'numpy==1.12.0', 'SQLAlchemy==1.1.5', 'websocket-client==0.40.0'],
=======
    install_requires=['zaifapi==1.3.1', 'numpy==1.12.0', 'SQLAlchemy==1.1.5', 'docopt==0.6.2'],
>>>>>>> 12dbeebf2d3b0824312d63962781ca077393d6d1
    entry_points="""\
      [console_scripts]
      update_assignee_id = zaifbot:main
      """,
)
