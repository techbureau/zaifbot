from setuptools import setup, find_packages

setup(
    name='zaifbot',
    version='0.0.0.dev3',
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
    install_requires=['zaifapi==1.5.1', 'numpy==1.12.0', 'SQLAlchemy==1.1.5', 'websocket-client==0.40.0'],
    entry_points="""\
      [console_scripts]
      update_assignee_id = zaifbot:main
      """,
    include_package_data=True
)
