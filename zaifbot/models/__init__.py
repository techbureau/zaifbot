from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


def get_connection_string():
    # マルチデータベースを実現したい場合、ここを修正する
    return 'sqlite:///{}'.format('zaif_bot.db')


Base = declarative_base()
engine = create_engine(get_connection_string())
metadata = MetaData(engine)
Session = sessionmaker(bind=engine)


def get_session():
    return Session()
