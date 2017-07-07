import os
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker


def __db_path():
    current_dir = os.path.dirname(__file__)
    parent_dir = os.path.abspath(os.path.join(current_dir, os.path.pardir))
    return 'sqlite:///{}'.format(os.path.join(parent_dir, 'zaifbot.db'))


def _get_engine(file_path):
    my_engine = None

    def _create_engine():
        nonlocal my_engine
        if my_engine:
            return my_engine
        my_engine = create_engine(file_path)
        return my_engine
    my_engine = _create_engine()
    return my_engine


engine = _get_engine(__db_path())
metadata = MetaData(bind=engine)

Session = sessionmaker(bind=engine)


def get_session():
    return Session()
